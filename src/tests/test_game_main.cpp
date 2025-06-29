#define DOCTEST_CONFIG_IMPLEMENT

#include "test_game_main.h"

#include <doctest.h>

#include <godot_cpp/classes/os.hpp>
#include <godot_cpp/templates/local_vector.hpp>
#include <godot_cpp/variant/packed_string_array.hpp>

#include "test_custom_sprite.h"

using namespace godot;

int godot::test_game_main(bool &tests_need_run) {
	PackedStringArray cmd_line_args = OS::get_singleton()->get_cmdline_args();

	LocalVector<String> test_args;
	for (const String &s : cmd_line_args) {
		if (s == "--game-test") {
			tests_need_run = true;
		} else {
			test_args.push_back(s);
		}
	}

	if (!tests_need_run) {
		return 0;
	}

	doctest::Context context;

	if (test_args.size() > 0) {
		// Convert Godot command line arguments back to standard arguments.
		char **doctest_args = new char *[test_args.size()];
		for (uint32_t x = 0; x < test_args.size(); x++) {
			// Operation to convert Godot string to non wchar string.
			CharString cs = test_args[x].utf8();
			const char *str = cs.get_data();
			// Allocate the string copy.
			doctest_args[x] = new char[strlen(str) + 1];
			// Copy this into memory.
			memcpy(doctest_args[x], str, strlen(str) + 1);
		}

		context.applyCommandLine(test_args.size(), doctest_args);

		for (uint32_t x = 0; x < test_args.size(); x++) {
			delete[] doctest_args[x];
		}
		delete[] doctest_args;
	}

	int result = context.run();
	if (context.shouldExit()) {
		return result;
	}

	return result;
}
