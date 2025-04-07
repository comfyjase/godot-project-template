#include "imgui_debug.h"

#include <godot_cpp/godot.hpp>

#if IMGUI_ENABLED
#include <imgui-godot.h>
#endif

using namespace godot;

void ImGuiDebug::_bind_methods()
{}

ImGuiDebug::ImGuiDebug() :
		selected_node(nullptr),
		any_hierarchy_item_selected(false)
{}

ImGuiDebug::~ImGuiDebug()
{}

void ImGuiDebug::_process(double delta)
{
#if IMGUI_ENABLED
	ImVec2 top_center = ImVec2(ImGui::GetMainViewport()->GetCenter().x, 0.0f);
	ImGui::SetNextWindowPos(top_center, ImGuiCond_Appearing, ImVec2(0.5f, 0.0f));
	ImGui::SetNextWindowBgAlpha(0.5f);

	// General Build Information
	ImGui::Begin("BuildInformation", 0, ImGuiWindowFlags_NoMove | ImGuiWindowFlags_NoResize | ImGuiWindowFlags_NoTitleBar);
	{
#if DEBUG
		ImGui::Text("Debug Build");
#elif RELEASE
		ImGui::Text("Release Build");
#elif PROFILE
		ImGui::Text("Profile Build");
#elif PRODUCTION
		ImGui::Text("Production Build");
#endif
		double fps = 1.0 / delta;
		ImGui::Text("FPS: %.2f", fps);
	}
	ImGui::End();

	// Game Specific Debug
	Node *root_node = find_parent("/root");
	ERR_FAIL_NULL_MSG(root_node, "Does the scene have any nodes?");

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
	}

	if (selected_node == node)
	{
		flag |= ImGuiTreeNodeFlags_Selected;
		any_hierarchy_item_selected = true;
	}

	const char* node_name = node->get_name().c_unescape().utf8().get_data();
	if (ImGui::TreeNodeEx(node_name, flag))
	{
		if (ImGui::IsItemClicked())
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
