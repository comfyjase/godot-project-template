#include "game_test_node.h"

#include <godot_cpp/classes/scene_tree.hpp>

#if TESTS_ENABLED
#include "test_game_main.h"
#endif

using namespace godot;

void GameTest::_bind_methods() {}

GameTest::GameTest() : Node() {}

GameTest::~GameTest() {}

void GameTest::_ready() {
	Node::_ready();

#if TESTS_ENABLED
	int test_results = test_game_main();
	if (test_results != 0) {
		print_error("Error: Game unit tests failed.");
	}
	get_tree()->quit(test_results);
#endif
}
