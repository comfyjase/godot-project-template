#include "register_types.h"

#include <gdextension_interface.h>
#include <godot_cpp/core/class_db.hpp>
#include <godot_cpp/core/defs.hpp>
#include <godot_cpp/godot.hpp>

#if IMGUI_ENABLED
#include <imgui-godot.h>
#endif

#include "build_information.h"
#include "function_library.h"
#include "macros.h"

using namespace godot;

void initialize_core_gdextension_types(ModuleInitializationLevel p_level) {
	if (p_level != MODULE_INITIALIZATION_LEVEL_SCENE) {
		return;
	}
	
#if IMGUI_ENABLED
	ImGui::Godot::SyncImGuiPtrs();
#endif

	GD_REGISTER_SINGLETON(FunctionLibrary);
	GDREGISTER_RUNTIME_CLASS(BuildInformation);
	
	development_cleanup_temp_project_plugin_files();
}

void uninitialize_core_gdextension_types(ModuleInitializationLevel p_level) {
	if (p_level != MODULE_INITIALIZATION_LEVEL_SCENE) {
		return;
	}
	
	GD_UNREGISTER_SINGLETON(FunctionLibrary);
}

extern "C" {
	// Initialization
	GDExtensionBool GDE_EXPORT core_library_init(GDExtensionInterfaceGetProcAddress p_get_proc_address, GDExtensionClassLibraryPtr p_library, GDExtensionInitialization *r_initialization) {
		GDExtensionBinding::InitObject init_obj(p_get_proc_address, p_library, r_initialization);
		init_obj.register_initializer(initialize_core_gdextension_types);
		init_obj.register_terminator(uninitialize_core_gdextension_types);
		init_obj.set_minimum_library_initialization_level(MODULE_INITIALIZATION_LEVEL_SCENE);
		return init_obj.init();
	}
}
