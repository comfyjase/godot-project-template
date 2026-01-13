#pragma once

#include <godot_cpp/classes/dir_access.hpp>
#include <godot_cpp/classes/engine.hpp>
#include <godot_cpp/classes/file_access.hpp>
#include <godot_cpp/classes/global_constants.hpp>
#include <godot_cpp/classes/input_event.hpp>
#include <godot_cpp/classes/node.hpp>
#include <godot_cpp/classes/object.hpp>
#include <godot_cpp/classes/project_settings.hpp>
#include <godot_cpp/classes/ref.hpp>
#include <godot_cpp/core/defs.hpp>
#include <godot_cpp/variant/array.hpp>
#include <godot_cpp/variant/packed_string_array.hpp>
#include <godot_cpp/variant/string.hpp>
#include <godot_cpp/variant/typed_array.hpp>
#include <godot_cpp/variant/variant.hpp>
#include <godot_cpp/variant/vector3.hpp>

#include "input_enums.h"
#include "macros.h"

namespace godot {

static void development_cleanup_temp_project_plugin_files() {
#if DEVELOPMENT
	GD_LOCAL_PTR(engine, Engine::get_singleton());

	if (engine->is_editor_hint()) {
		GD_LOCAL_PTR(project_settings, ProjectSettings::get_singleton());

		const String &folder_path_to_cleaup = "res://bin/temp";
		const String &absolute_folder_path_to_cleanup = project_settings->globalize_path(folder_path_to_cleaup);

		if (DirAccess::dir_exists_absolute(absolute_folder_path_to_cleanup)) {
			Ref<DirAccess> dir = DirAccess::open(absolute_folder_path_to_cleanup);
			const PackedStringArray &files = dir->get_files();

			auto remove_file = [&](const String &p_file_name) {
				const String &absolute_file_path = absolute_folder_path_to_cleanup + String("/") + p_file_name;
				if (FileAccess::file_exists(absolute_file_path)) {
					dir->remove(absolute_file_path);
				}
			};

			// Note: Starting from 1 to skip over the .gdignore file.
			// That file should be removed when it's the only remaining file in the temp directory.
			for (int i = 1; i < files.size(); ++i) {
				remove_file(files[i]);
			}

			if (dir->get_files().size() == 1) {
				const String &file_name = dir->get_files()[0];
				if (file_name == ".gdignore") {
					remove_file(file_name);
					DirAccess::remove_absolute(absolute_folder_path_to_cleanup);
				}
			}
		}
	}
#endif
}

class FunctionLibrary : public Object {
	GDCLASS(FunctionLibrary, Object);

protected:
	static void _bind_methods();

public:
	static void create_singleton();
	static void free_singleton();
	static FunctionLibrary *get_singleton();

	FunctionLibrary();

	bool is_equal_approx(const Vector3 &p_vector3_a, const Vector3 &p_vector3_b, const float p_tolerance = 0.1f) const;

	void get_input_device(const Ref<InputEvent> &p_input_event, InputDevice::Type &p_out_input_device);

	template <typename T>
	T *find_node(Node *root_node) {
		ERR_FAIL_NULL_V_MSG(root_node, nullptr, "FunctionLibrary::find_node<T> parameter root_node is nullptr.");

		T *node = Object::cast_to<T>(root_node);
		if (node) {
			return node;
		}

		TypedArray<Node> children_nodes = root_node->get_children();
		for (int i = 0; i < children_nodes.size(); ++i) {
			Variant child_node_variant = children_nodes[i];

			T *child_node = Object::cast_to<T>(child_node_variant);
			if (child_node) {
				return child_node;
				// Recursively checks children nodes.
			} else {
				child_node = find_node<T>(Object::cast_to<Node>(child_node_variant));
				if (child_node)
					return child_node;
			}
		}

		return nullptr;
	}

	template <typename T>
	TypedArray<T> find_nodes(Node *root_node) {
		TypedArray<T> nodes;

		ERR_FAIL_NULL_V_MSG(root_node, nodes, "FunctionLibrary::find_nodes<T> parameter root_node is nullptr.");

		T *node = Object::cast_to<T>(root_node);
		if (node) {
			nodes.append(node);
		}

		TypedArray<Node> children_nodes = root_node->get_children();
		for (int i = 0; i < children_nodes.size(); ++i) {
			Variant child_node_variant = children_nodes[i];

			T *child_node = Object::cast_to<T>(child_node_variant);
			if (child_node) {
				nodes.append(child_node);
				// Recursively checks children nodes.
			} else {
				nodes.append_array(find_nodes<T>(Object::cast_to<Node>(child_node_variant)));
			}
		}

		return nodes;
	}

private:
	static FunctionLibrary *singleton;
};

} //namespace godot
