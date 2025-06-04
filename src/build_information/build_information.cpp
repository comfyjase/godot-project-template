#include "build_information.h"

#include <godot_cpp/core/class_db.hpp>
#include <godot_cpp/core/print_string.hpp>
#include <godot_cpp/classes/engine.hpp>
#include <godot_cpp/classes/file_access.hpp>
#include <godot_cpp/classes/global_constants.hpp>
#include <godot_cpp/classes/input.hpp>
#include <godot_cpp/classes/label.hpp>
#include <godot_cpp/classes/rendering_server.hpp>
#include <godot_cpp/classes/rich_text_label.hpp>
#include <godot_cpp/classes/scene_tree.hpp>
#include <godot_cpp/classes/viewport.hpp>

#if IMGUI_ENABLED
#include <imgui-godot.h>
#endif

using namespace godot;

void BuildInformation::_bind_methods()
{}

BuildInformation::BuildInformation() :
		always_show_build_information(true),
		cpu_times(),
		gpu_times(),
		current_frame_history_index(0),
		input(nullptr),
		rendering_server(nullptr),
		viewport(nullptr),
		viewport_rid(),
		selected_node(nullptr),
		any_hierarchy_item_selected(false),
		build_name_label(nullptr),
		fps_label(nullptr),
		frame_time_label(nullptr),
		cpu_frame_time_label(nullptr),
		gpu_frame_time_label(nullptr),
		joypad_button_just_pressed(false),
		show(false)
{}

BuildInformation::~BuildInformation()
{}

void BuildInformation::_ready()
{
#if IMGUI_ENABLED
	ImGui::GetIO().ConfigFlags |= ImGuiConfigFlags_NavEnableGamepad;
#endif

	input = Input::get_singleton();
	ERR_FAIL_NULL_MSG(input, "Input hasn't been initialized yet?");

	viewport = get_viewport();
	ERR_FAIL_NULL_MSG(viewport, "Viewport hasn't been initialized yet?");
	viewport_rid = viewport->get_viewport_rid();

	rendering_server = RenderingServer::get_singleton();
	ERR_FAIL_NULL_MSG(rendering_server, "Rendering server is invalid");
	rendering_server->viewport_set_measure_render_time(viewport_rid, true);

	const double initial_frame_time = (1000.0 / 120.0);
	for (int i = 0; i < FRAME_TIME_HISTORY; ++i)
	{
		cpu_times[i] = initial_frame_time;
		gpu_times[i] = initial_frame_time;
	}

	current_frame_history_index = 0;

	Vector2 debug_ui_minimum_size = Vector2(30.0f, 30.0f);

	// Build Name
	String build_information_file_path = "res://bin/build.info";
	String build_name = FileAccess::open(build_information_file_path, FileAccess::READ)->get_as_text();
	build_name_label = memnew(Label);
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

void BuildInformation::_input(const Ref<InputEvent> &p_event)
{
#if IMGUI_ENABLED
	bool imgui_toggle_debug_joypad_input = (input->is_joy_button_pressed(0, JoyButton::JOY_BUTTON_LEFT_STICK) && input->is_joy_button_pressed(0, JoyButton::JOY_BUTTON_RIGHT_STICK));

	// Keyboard input
	if (input->is_action_just_pressed("imgui_toggle_debug"))
	{
		show = !show;
	}

	// Joypad input
	if (imgui_toggle_debug_joypad_input)
	{
		if (!joypad_button_just_pressed)
		{
			show = !show;
			joypad_button_just_pressed = true;
		}
	}
	else
	{
		joypad_button_just_pressed = false;
	}
#endif
}

void BuildInformation::_process(double delta)
{
	if (!show)
	{
		if (always_show_build_information)
		{
			draw_build_information(delta);
		}

		return;
	}

	// Build Information
	// Things such as build type, FPS and frame times
	draw_build_information(delta);

#if IMGUI_ENABLED
	// Game Specific Debug
	SceneTree *scene_tree = get_tree();
	ERR_FAIL_NULL_MSG(scene_tree, "Failed to get scene tree somehow");
	Node *root_node = scene_tree->get_current_scene();
	ERR_FAIL_NULL_MSG(root_node, "Failed to find root node somehow");

	ImGui::Begin("Scene Hierarchy");
	{
		any_hierarchy_item_selected = false;

		draw_node_hierarchy(root_node);

		if (!any_hierarchy_item_selected)
		{
			selected_node = nullptr;
		}
	}
	ImGui::End();

	if (selected_node != nullptr && root_node != selected_node && selected_node->has_method("draw_debug"))
	{
		ImGui::Begin("Debug Menu");
		{
			draw_debug_menu(selected_node);
		}
		ImGui::End();
	}
#endif
}

void BuildInformation::init_build_information_rich_text_label(RichTextLabel *&rich_text_label, String label_name, const Vector2 &size) {
	rich_text_label = memnew(RichTextLabel);
	rich_text_label->set_name(label_name);
	rich_text_label->set_horizontal_alignment(HorizontalAlignment::HORIZONTAL_ALIGNMENT_RIGHT);
	rich_text_label->set_fit_content(true);
	rich_text_label->set_custom_minimum_size(size);
	rich_text_label->set_size(size);
	rich_text_label->set_use_bbcode(true);
	add_child(rich_text_label);
}

void BuildInformation::draw_build_information(double delta) {
	const double fps = 1.0 / delta;

	String text_colour = "green";
	if (fps <= 10.0)
		text_colour = "red";
	else if (fps < 60.0)
		text_colour = "yellow";
	fps_label->set_text("FPS: [color=" + text_colour + "]" + String::num_real(fps).pad_decimals(2) + "[/color]");

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

void BuildInformation::draw_node_hierarchy(Node *node)
{
#if IMGUI_ENABLED
	ImGuiTreeNodeFlags flag = ImGuiTreeNodeFlags_DefaultOpen;

	if (node->get_child_count() == 0)
	{
		flag |= ImGuiTreeNodeFlags_Leaf;
	}
	else
	{
		flag |= ImGuiTreeNodeFlags_OpenOnArrow;
		flag |= ImGuiTreeNodeFlags_OpenOnDoubleClick;
	}

	if (selected_node == node)
	{
		flag |= ImGuiTreeNodeFlags_Selected;
		any_hierarchy_item_selected = true;
	}

	if (ImGui::TreeNodeEx(node->get_name().c_unescape().utf8().get_data(), flag))
	{
		if (ImGui::IsItemClicked() || ImGui::IsItemActivated())
		{
			selected_node = node;
			any_hierarchy_item_selected = true;
		}
		
		Array children_nodes = node->get_children();
		for (int i = 0; i < children_nodes.size(); ++i)
		{
			Node* child = node->get_child(i);
			draw_node_hierarchy(child);
		}

		ImGui::TreePop();
	}
#endif
}

void BuildInformation::draw_debug_menu(Node *node, bool include_all_children_draw_debug/* = false*/)
{
#if IMGUI_ENABLED
	if (node->has_method("draw_debug"))
	{
		ImGui::Text("%s", node->get_name().c_unescape().utf8().get_data());
		ImGui::Separator();
		node->call("draw_debug");
		ImGui::Separator();
	}

	if (include_all_children_draw_debug)
	{
		TypedArray<Node> children_nodes = node->get_children();
		for (int i = 0; i < children_nodes.size(); ++i)
		{
			Node* child = node->get_child(i);
			draw_debug_menu(child, include_all_children_draw_debug);
		}
	}
#endif
}
