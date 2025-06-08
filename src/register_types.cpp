#include "register_types.h"

#include <gdextension_interface.h>
#include <godot_cpp/core/class_db.hpp>
#include <godot_cpp/core/defs.hpp>
#include <godot_cpp/godot.hpp>

#if IMGUI_ENABLED
#include <imgui-godot.h>
#endif

#include "custom_sprite.h"
#include "build_information.h"
#if TESTS_ENABLED
#include "tests/game_test_node.h"
#endif

using namespace godot;

void initialize_gdextension_types(ModuleInitializationLevel p_level) {
	if (p_level != MODULE_INITIALIZATION_LEVEL_SCENE) {
		return;
	}

#if IMGUI_ENABLED
	ImGui::Godot::SyncImGuiPtrs();
#endif

	// Use GDREGISTER_CLASS if you want logic to run in editor as well...
	GDREGISTER_RUNTIME_CLASS(BuildInformation);
	GDREGISTER_CLASS(CustomSprite);
	
#if TESTS_ENABLED
	GDREGISTER_RUNTIME_CLASS(GameTest);
#endif
}

void uninitialize_gdextension_types(ModuleInitializationLevel p_level) {
	if (p_level != MODULE_INITIALIZATION_LEVEL_SCENE) {
		return;
	}
}

extern "C" {
// Initialization
GDExtensionBool GDE_EXPORT game_library_init(GDExtensionInterfaceGetProcAddress p_get_proc_address, GDExtensionClassLibraryPtr p_library, GDExtensionInitialization *r_initialization) {
	GDExtensionBinding::InitObject init_obj(p_get_proc_address, p_library, r_initialization);
	init_obj.register_initializer(initialize_gdextension_types);
	init_obj.register_terminator(uninitialize_gdextension_types);
	init_obj.set_minimum_library_initialization_level(MODULE_INITIALIZATION_LEVEL_SCENE);

	return init_obj.init();
}
}
