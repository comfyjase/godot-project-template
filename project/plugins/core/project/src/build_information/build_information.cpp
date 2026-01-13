#include "build_information.h"

#include <godot_cpp/classes/display_server.hpp>
#include <godot_cpp/classes/engine.hpp>
#include <godot_cpp/classes/file_access.hpp>
#include <godot_cpp/classes/global_constants.hpp>
#include <godot_cpp/classes/input.hpp>
#include <godot_cpp/classes/label.hpp>
#include <godot_cpp/classes/object.hpp>
#include <godot_cpp/classes/os.hpp>
#include <godot_cpp/classes/project_settings.hpp>
#include <godot_cpp/classes/rendering_server.hpp>
#include <godot_cpp/classes/rich_text_label.hpp>
#include <godot_cpp/classes/scene_tree.hpp>
#include <godot_cpp/classes/viewport.hpp>
#include <godot_cpp/core/class_db.hpp>
#include <godot_cpp/core/print_string.hpp>
#include <godot_cpp/variant/variant.hpp>

#if IMGUI_ENABLED
#include <imgui-godot.h>
#endif

#include "macros.h"

using namespace godot;

void BuildInformation::_bind_methods() {
	GD_BIND_METHOD(BuildInformation, register_debug_system, "p_debug_system");
	GD_BIND_METHOD(BuildInformation, unregister_debug_system, "p_debug_system");
}

BuildInformation::BuildInformation() :
		always_show_build_information(true),
		cpu_times(),
		gpu_times(),
		current_frame_history_index(0),
		debug_systems(),
		input(nullptr),
		rendering_server(nullptr),
		viewport(nullptr),
		viewport_rid(),
		selected_node(nullptr),
		any_hierarchy_item_selected(false),
		only_show_nodes_with_debug_draw_available(true),
		build_name_label(nullptr),
		fps_label(nullptr),
		frame_time_label(nullptr),
		cpu_frame_time_label(nullptr),
		gpu_frame_time_label(nullptr),
		joypad_show_imgui_debug_button_just_pressed(false),
		joypad_focus_imgui_debug_button_just_pressed(false),
		show(false),
		focus(true) {}

BuildInformation::~BuildInformation() {}

void BuildInformation::_ready() {
	GD_PTR(input, Input::get_singleton());
	GD_PTR(rendering_server, RenderingServer::get_singleton());
	GD_PTR(viewport, get_viewport());
	GD_PTR(build_name_label, memnew(Label));
	GD_PTR(fps_label, memnew(RichTextLabel));
	GD_PTR(frame_time_label, memnew(RichTextLabel));
	GD_PTR(cpu_frame_time_label, memnew(RichTextLabel));
	GD_PTR(gpu_frame_time_label, memnew(RichTextLabel));
	GD_LOCAL_PTR(project_settings, ProjectSettings::get_singleton());

	viewport_rid = viewport->get_viewport_rid();
	rendering_server->viewport_set_measure_render_time(viewport_rid, true);

	const double initial_frame_time = (1000.0 / 120.0);
	for (int i = 0; i < FRAME_TIME_HISTORY; ++i) {
		cpu_times[i] = initial_frame_time;
		gpu_times[i] = initial_frame_time;
	}

	current_frame_history_index = 0;

	// Mobiles only to make sure build info appears in the edges of the screen
	// Even if the device has rounded corners.
#if PLATFORM_IOS || PLATFORM_ANDROID
	static constexpr float padding = 30.0f;
	set_position(Vector2(get_position().x - padding, get_position().y + padding));
#endif

	Vector2 debug_ui_minimum_size = Vector2(30.0f, 30.0f);

	// Build Name
	const String &build_information_file_path = "res://bin/build.info";
	const String &build_information_file_as_text = FileAccess::open(build_information_file_path, FileAccess::READ)->get_as_text();

	const String &version_number = String(project_settings->get_setting("application/config/version"));
	const int64_t first_underscore_index = build_information_file_as_text.find("_");
	const String &build_name = build_information_file_as_text.insert(first_underscore_index, String("_v") + version_number);

	build_name_label->set_name("BuildNameLabel");
	build_name_label->set_horizontal_alignment(HorizontalAlignment::HORIZONTAL_ALIGNMENT_RIGHT);
	build_name_label->set_text(build_name);
	build_name_label->set_custom_minimum_size(debug_ui_minimum_size);
	build_name_label->set_size(debug_ui_minimum_size);
	add_child(build_name_label);

	debug_ui_minimum_size = Vector2(20.0f, 20.0f);
	// FPS
	init_build_information_rich_text_label(fps_label, "FPSLabel", debug_ui_minimum_size);
	// Frame Time
	init_build_information_rich_text_label(frame_time_label, "FrameTimeLabel", debug_ui_minimum_size);
	// CPU Frame Time
	init_build_information_rich_text_label(cpu_frame_time_label, "CPUFrameTimeLabel", debug_ui_minimum_size);
	// GPU Frame Time
	init_build_information_rich_text_label(gpu_frame_time_label, "GPUFrameTimeLabel", debug_ui_minimum_size);
}

void BuildInformation::_unhandled_input(const Ref<InputEvent> &p_event) {
#if IMGUI_ENABLED
	ERR_FAIL_NULL(input);

	GD_LOCAL_PTR(viewport, get_viewport());

	const bool imgui_toggle_debug_joypad_input = (input->is_joy_button_pressed(0, JoyButton::JOY_BUTTON_LEFT_STICK) && input->is_joy_button_pressed(0, JoyButton::JOY_BUTTON_RIGHT_STICK));
	const bool imgui_toggle_focus_joypad_input = (input->is_joy_button_pressed(0, JoyButton::JOY_BUTTON_LEFT_STICK) && input->is_joy_button_pressed(0, JoyButton::JOY_BUTTON_DPAD_DOWN));

	// Keyboard input
	if (input->is_action_just_pressed("imgui_toggle_debug")) {
		show = !show;

		if (show) {
			// Always focus when explicitly showing the debug menu.
			focus = true;
			on_enable_focus();
		} else {
			focus = false;
			on_disable_focus();
		}

		viewport->set_input_as_handled();
		return;
	}

	if (input->is_action_just_pressed("imgui_toggle_focus")) {
		focus = !focus;

		if (focus) {
			on_enable_focus();
		} else {
			on_disable_focus();
		}

		viewport->set_input_as_handled();
		return;
	}

	// Joypad input
	if (imgui_toggle_debug_joypad_input) {
		if (!joypad_show_imgui_debug_button_just_pressed) {
			show = !show;
			joypad_show_imgui_debug_button_just_pressed = true;

			if (show) {
				focus = true;
				on_enable_focus();
			} else {
				focus = false;
				on_disable_focus();
			}
			viewport->set_input_as_handled();
			return;
		}
	} else {
		joypad_show_imgui_debug_button_just_pressed = false;
	}

	if (imgui_toggle_focus_joypad_input) {
		if (!joypad_focus_imgui_debug_button_just_pressed) {
			focus = !focus;
			joypad_focus_imgui_debug_button_just_pressed = true;

			if (focus) {
				on_enable_focus();
			} else {
				on_disable_focus();
			}

			viewport->set_input_as_handled();
		}
	} else {
		joypad_focus_imgui_debug_button_just_pressed = false;
	}
#endif
}

void BuildInformation::_process(double delta) {
	if (!show) {
		if (always_show_build_information) {
			draw_build_information(delta);
		}

		return;
	}

	// Build Information
	// Things such as build type, FPS and frame times
	draw_build_information(delta);

#if IMGUI_ENABLED
	auto interpolate_func = [&](float x, float minInput, float maxInput, float minOutput, float maxOutput) -> float {
		// clamp values outside the range
		if (x <= minInput)
			x = minInput;
		if (x >= maxInput)
			x = maxInput;

		// normalize x
		float t = (x - minInput) / (maxInput - minInput);

		// interpolate
		return minOutput + (maxOutput - minOutput) * t;
	};

	const int MIN_WIDTH_SUPPORTED = 1080; // FHD width
	const int MAX_WIDTH_SUPPORTED = 3840; // 4K width
	const float MIN_SCALE = 1.0;
	const float MAX_SCALE = 1.5;

	const Vector2i &screen_size = DisplayServer::get_singleton()->screen_get_size();
	float global_font_ui_scale = interpolate_func(screen_size.x, MIN_WIDTH_SUPPORTED, MAX_WIDTH_SUPPORTED, MIN_SCALE, MAX_SCALE);
	ImGuiIO &io = ImGui::GetIO();
	io.FontGlobalScale = global_font_ui_scale;

	GD_LOCAL_PTR(scene_tree, get_tree());
	GD_LOCAL_PTR(root_node, scene_tree->get_current_scene());

	if (focus) {
		ImVec4 focused_colour = ImGui::GetStyle().Colors[ImGuiCol_WindowBg];
		focused_colour.w = 1.0f;
		ImGui::GetStyle().Colors[ImGuiCol_WindowBg] = focused_colour;
	} else {
		ImVec4 not_focused_colour = ImGui::GetStyle().Colors[ImGuiCol_WindowBg];
		not_focused_colour.w = 0.5f;
		ImGui::GetStyle().Colors[ImGuiCol_WindowBg] = not_focused_colour;
	}

	// Game Specific Debug
	ImGui::Begin("Scene Hierarchy");
	{
		ImGui::Checkbox("Only Show Nodes With Debug Draw Available", &only_show_nodes_with_debug_draw_available);

		any_hierarchy_item_selected = false;

		draw_node_hierarchy(root_node);

		if (!any_hierarchy_item_selected) {
			selected_node = nullptr;
		}
	}
	ImGui::End();

	if (selected_node != nullptr && root_node != selected_node && selected_node->has_method("draw_debug")) {
		ImGui::Begin("Selected Node Debug Menu");
		{
			draw_debug_menu(selected_node);
		}
		ImGui::End();
	}

	ImGui::Begin("Debug Systems");
	{
		ImGui::BeginTabBar("##debug_systems_tabs");
		{
			for (int i = 0; i < debug_systems.size(); ++i) {
				Variant debug_system = debug_systems[i];
				if (debug_system.has_method("draw_debug")) {
					debug_system.call("draw_debug");
				}
			}
			ImGui::EndTabBar();
		}
	}
	ImGui::End();
#endif
}

void BuildInformation::register_debug_system(Object *p_debug_system) {
	ERR_FAIL_NULL(p_debug_system);
	debug_systems.append(p_debug_system);
}

void BuildInformation::unregister_debug_system(Object *p_debug_system) {
	ERR_FAIL_NULL(p_debug_system);
	debug_systems.erase(p_debug_system);
}

bool BuildInformation::is_showing() const {
	return show && focus;
}

void BuildInformation::init_build_information_rich_text_label(RichTextLabel *rich_text_label, String label_name, const Vector2 &size) {
	rich_text_label->set_name(label_name);
	rich_text_label->set_horizontal_alignment(HorizontalAlignment::HORIZONTAL_ALIGNMENT_RIGHT);
	rich_text_label->set_fit_content(true);
	rich_text_label->set_custom_minimum_size(size);
	rich_text_label->set_size(size);
	rich_text_label->set_use_bbcode(true);
	add_child(rich_text_label);
}

void BuildInformation::draw_build_information(double delta) {
	ERR_FAIL_NULL(fps_label);
	ERR_FAIL_NULL(frame_time_label);
	ERR_FAIL_NULL(cpu_frame_time_label);
	ERR_FAIL_NULL(gpu_frame_time_label);
	ERR_FAIL_NULL(rendering_server);

	const double fps = 1.0 / delta;

	String text_colour = "green";
	if (fps <= 10.0)
		text_colour = "red";
	else if (fps < 60.0)
		text_colour = "yellow";
	fps_label->set_text("FPS: [color=" + text_colour + "]" + String::num_real(fps).pad_decimals(0) + "[/color]");

	const double frame_time = 1000.0 / fps;
	text_colour = "green";
	if (frame_time >= 100.0)
		text_colour = "red";
	else if (frame_time > 16.66)
		text_colour = "yellow";
	frame_time_label->set_text("Frame Time: [color=" + text_colour + "]" + String::num_real(frame_time).pad_decimals(2) + "ms[/color]");

	const double cpu_frame_time = rendering_server->viewport_get_measured_render_time_cpu(viewport_rid) + rendering_server->get_frame_setup_time_cpu();
	const double gpu_frame_time = rendering_server->viewport_get_measured_render_time_gpu(viewport_rid);
	cpu_times[current_frame_history_index] = cpu_frame_time;
	gpu_times[current_frame_history_index] = gpu_frame_time;

	double cpu_time = 0.0;
	for (int i = 0; i < FRAME_TIME_HISTORY; ++i) {
		cpu_time += cpu_times[i];
	}
	cpu_time /= FRAME_TIME_HISTORY;
	cpu_time = MAX(0.01, cpu_time);

	double gpu_time = 0.0;
	for (int i = 0; i < FRAME_TIME_HISTORY; ++i) {
		gpu_time += gpu_times[i];
	}
	gpu_time /= FRAME_TIME_HISTORY;
	gpu_time = MAX(0.01, gpu_time);

	text_colour = "green";
	if (cpu_time >= 15.0)
		text_colour = "red";
	else if (cpu_time > 7.0)
		text_colour = "yellow";
	cpu_frame_time_label->set_text("CPU Time: [color=" + text_colour + "]" + String::num_real(cpu_time).pad_decimals(2) + "ms[/color]");

	text_colour = "green";
	if (gpu_time >= 15.0)
		text_colour = "red";
	else if (gpu_time > 7.0)
		text_colour = "yellow";
	gpu_frame_time_label->set_text("GPU Time: [color=" + text_colour + "]" + String::num_real(gpu_time).pad_decimals(2) + "ms[/color]");

	++current_frame_history_index;
	if ((current_frame_history_index + 1) == FRAME_TIME_HISTORY)
		current_frame_history_index = 0;
}

void BuildInformation::draw_node_hierarchy(Node *node) {
#if IMGUI_ENABLED
	ERR_FAIL_NULL(node);

	ImGuiTreeNodeFlags flag = ImGuiTreeNodeFlags_DefaultOpen;
	if (node->get_child_count() == 0) {
		flag |= ImGuiTreeNodeFlags_Leaf;
	} else {
		flag |= ImGuiTreeNodeFlags_OpenOnArrow;
		flag |= ImGuiTreeNodeFlags_OpenOnDoubleClick;
	}
	if (selected_node == node) {
		flag |= ImGuiTreeNodeFlags_Selected;
		any_hierarchy_item_selected = true;
	}

	const String &node_name = node->get_name() + String("##") + String::num_uint64(node->get_instance_id());

	auto draw_node_and_children_func = [&]() {
		if (ImGui::TreeNodeEx(node_name.utf8().get_data(), flag)) {
			if (ImGui::IsItemClicked() || ImGui::IsItemActivated()) {
				selected_node = node;
				any_hierarchy_item_selected = true;
			}

			Array children_nodes = node->get_children();
			for (int i = 0; i < children_nodes.size(); ++i) {
				GD_LOCAL_PTR(child, node->get_child(i));
				draw_node_hierarchy(child);
			}

			ImGui::TreePop();
		}
	};

	if (only_show_nodes_with_debug_draw_available) {
		if (node->has_method("draw_debug")) {
			draw_node_and_children_func();
		} else {
			Array children_nodes = node->get_children();
			for (int i = 0; i < children_nodes.size(); ++i) {
				GD_LOCAL_PTR(child, node->get_child(i));
				draw_node_hierarchy(child);
			}
		}
	} else {
		draw_node_and_children_func();
	}
#endif
}

void BuildInformation::draw_debug_menu(Node *node, bool include_all_children_draw_debug /* = false*/) {
#if IMGUI_ENABLED
	ERR_FAIL_NULL(node);

	if (node->has_method("draw_debug")) {
		ImGui::Text("%s", node->get_name().c_unescape().utf8().get_data());
		ImGui::Separator();
		node->call("draw_debug");
		ImGui::Separator();
	}

	if (include_all_children_draw_debug) {
		TypedArray<Node> children_nodes = node->get_children();
		for (int i = 0; i < children_nodes.size(); ++i) {
			GD_LOCAL_PTR(child, node->get_child(i));
			draw_debug_menu(child, include_all_children_draw_debug);
		}
	}
#endif
}

void BuildInformation::on_enable_focus() {
#if IMGUI_ENABLED
	ERR_FAIL_NULL(input);

	input->set_mouse_mode(Input::MOUSE_MODE_VISIBLE);
	ImGui::GetIO().ConfigFlags |= ImGuiConfigFlags_NavEnableGamepad;
#endif
}

void BuildInformation::on_disable_focus() {
#if IMGUI_ENABLED
	ERR_FAIL_NULL(input);

	input->set_mouse_mode(Input::MOUSE_MODE_CAPTURED);
	ImGui::GetIO().ConfigFlags &= ~ImGuiConfigFlags_NavEnableGamepad;
#endif
}
