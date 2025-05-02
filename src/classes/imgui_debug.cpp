#include "imgui_debug.h"

#include <godot_cpp/core/class_db.hpp>
#include <godot_cpp/classes/engine.hpp>
#include <godot_cpp/classes/global_constants.hpp>
#include <godot_cpp/classes/input.hpp>
#include <godot_cpp/classes/rendering_server.hpp>
#include <godot_cpp/classes/scene_tree.hpp>
#include <godot_cpp/classes/viewport.hpp>

#if IMGUI_ENABLED
#include <imgui-godot.h>
#endif

using namespace godot;

void ImGuiDebug::_bind_methods()
{}

ImGuiDebug::ImGuiDebug() :
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
		joypad_button_just_pressed(false),
		show(false)
{}

ImGuiDebug::~ImGuiDebug()
{}

void ImGuiDebug::_ready()
{
#if IMGUI_ENABLED
	ImGui::GetIO().ConfigFlags |= ImGuiConfigFlags_NavEnableGamepad;

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
#endif
}

void ImGuiDebug::_input(const Ref<InputEvent> &p_event)
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

void ImGuiDebug::_process(double delta)
{
#if IMGUI_ENABLED
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

void godot::ImGuiDebug::draw_build_information(double delta)
{
#if IMGUI_ENABLED
	static const ImVec4 GOOD_COLOUR = ImVec4(0.0f, 1.0f, 0.0f, 1.0f);	// Green
	static const ImVec4 OKAY_COLOUR = ImVec4(1.0f, 1.0f, 0.0f, 1.0f);	// Yellow
	static const ImVec4 BAD_COLOUR = ImVec4(1.0f, 0.0f, 0.0f, 1.0f);	// Red

	const ImVec2 top_center = ImVec2(ImGui::GetMainViewport()->GetCenter().x, 0.0f);
	ImGui::SetNextWindowPos(top_center, ImGuiCond_Appearing, ImVec2(0.5f, 0.0f));
	ImGui::SetNextWindowSize({ 200, 150 }, ImGuiCond_Once);
	ImGui::SetNextWindowBgAlpha(0.5f);

	// General Build Information
	ImGui::Begin("BuildInformation", 0, ImGuiWindowFlags_NoMove | ImGuiWindowFlags_NoResize | ImGuiWindowFlags_NoTitleBar | ImGuiWindowFlags_NoNav | ImGuiWindowFlags_NoNavFocus | ImGuiWindowFlags_NoNavInputs);
	{
		String platform = "None";
#if PLATFORM_WIN32
#error Win32 isn't supported by imgui-godot and doesn't have IMGUI_ENABLED defined
		return;
#elif PLATFORM_WIN64
		platform = "Win64";
#elif PLATFORM_LINUX
		platform = "Linux";
#elif PLATFORM_MACOS
		platform = "MacOS";
#else
		#error Unsupported platform, should IMGUI_ENABLED by defined for this platform?
		return;
#endif

		String configuration = "None";
#if DEBUG
		configuration = "Debug";
#elif RELEASE
		configuration = "Release";
#elif PROFILE
		configuration = "Profile";
#elif PRODUCTION
		configuration = "Production";
#else
		#error Unsupported configuration
		return;
#endif

		String precision = "None";
#if REAL_T_IS_DOUBLE
		precision = "Double";
#else
		precision = "Single";
#endif

		ImGui::Text("%s %s Build", platform.c_unescape().utf8().get_data(),
			configuration.c_unescape().utf8().get_data());

		ImGui::Separator();

		ImGui::Text("Precision: %s", precision.c_unescape().utf8().get_data());

		ImGui::Separator();

		const double fps = 1.0 / delta;
		if (fps <= 10.0)
			ImGui::PushStyleColor(ImGuiCol_Text, BAD_COLOUR);
		else if (fps < 60.0)
			ImGui::PushStyleColor(ImGuiCol_Text, OKAY_COLOUR);
		else
			ImGui::PushStyleColor(ImGuiCol_Text, GOOD_COLOUR);
		ImGui::Text("FPS: %.2f", fps);
		ImGui::PopStyleColor();

		const double frame_time = 1000.0 / fps;
		if (frame_time >= 100.0)
			ImGui::PushStyleColor(ImGuiCol_Text, BAD_COLOUR);
		else if (frame_time > 16.66)
			ImGui::PushStyleColor(ImGuiCol_Text, OKAY_COLOUR);
		else
			ImGui::PushStyleColor(ImGuiCol_Text, GOOD_COLOUR);
		ImGui::Text("Frame Time: %.2fms", frame_time);
		ImGui::PopStyleColor();

		const double cpu_frame_time = rendering_server->viewport_get_measured_render_time_cpu(viewport_rid) + rendering_server->get_frame_setup_time_cpu();
		const double gpu_frame_time = rendering_server->viewport_get_measured_render_time_gpu(viewport_rid);
		cpu_times[current_frame_history_index] = cpu_frame_time;
		gpu_times[current_frame_history_index] = gpu_frame_time;

		double cpu_time = 0.0;
		for (int i = 0; i < FRAME_TIME_HISTORY; ++i)
		{
			cpu_time += cpu_times[i];
		}
		cpu_time /= FRAME_TIME_HISTORY;
		cpu_time = MAX(0.01, cpu_time);

		double gpu_time = 0.0;
		for (int i = 0; i < FRAME_TIME_HISTORY; ++i)
		{
			gpu_time += gpu_times[i];
		}
		gpu_time /= FRAME_TIME_HISTORY;
		gpu_time = MAX(0.01, gpu_time);

		if (cpu_time >= 15.0)
			ImGui::PushStyleColor(ImGuiCol_Text, BAD_COLOUR);
		else if (cpu_time > 7.0)
			ImGui::PushStyleColor(ImGuiCol_Text, OKAY_COLOUR);
		else
			ImGui::PushStyleColor(ImGuiCol_Text, GOOD_COLOUR);
		ImGui::Text("CPU Time: %.2fms", cpu_time);
		ImGui::PopStyleColor();

		if (gpu_time >= 15.0)
			ImGui::PushStyleColor(ImGuiCol_Text, BAD_COLOUR);
		else if (gpu_time > 7.0)
			ImGui::PushStyleColor(ImGuiCol_Text, OKAY_COLOUR);
		else
			ImGui::PushStyleColor(ImGuiCol_Text, GOOD_COLOUR);
		ImGui::Text("GPU Time: %.2fms", gpu_time);
		ImGui::PopStyleColor();
	}
	ImGui::End();

	++current_frame_history_index;
	if ((current_frame_history_index + 1) == FRAME_TIME_HISTORY)
		current_frame_history_index = 0;
#endif
}

void ImGuiDebug::draw_node_hierarchy(Node *node)
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

void ImGuiDebug::draw_debug_menu(Node *node, bool include_all_children_draw_debug/* = false*/)
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
