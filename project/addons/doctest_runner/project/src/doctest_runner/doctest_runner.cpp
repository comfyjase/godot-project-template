#include "doctest_runner.h"

#include <godot_cpp/classes/scene_tree.hpp>
#include <godot_cpp/variant/typed_array.hpp>

#include "macros.h"

using namespace godot;

void DoctestRunner::_bind_methods() {}

DoctestRunner::DoctestRunner() :
		Node(),
		number_of_finished_test_runs(0),
		return_code(0) {}

DoctestRunner::~DoctestRunner() {}

void DoctestRunner::_ready() {
	Node::_ready();

	const TypedArray<Node> &children = get_children();
	print_line(vformat("[DoctestRunner] - %s tests to run", String::num_int64(get_child_count())));

	for (int i = 0; i < children.size(); ++i) {
		GD_LOCAL_PTR(child, Object::cast_to<Node>(children[i]));
		GD_CONNECT_SIGNAL(child, "tests_finished", &DoctestRunner::test_runner_finished);

		if (child->has_method("run_tests")) {
			print_line(vformat("[DoctestRunner] - %s starting tests", child->get_name()));
			child->call("run_tests");
		} else {
			print_error(vformat("[DoctestRunner] - Child %s doesn't have a run_tests method implemented - unit tests won't run for this node.", child->get_name()));
		}
	}
}

void DoctestRunner::test_runner_finished(Node *p_node, int p_return_code) {
	ERR_FAIL_NULL(p_node);

	return_code += p_return_code;
	number_of_finished_test_runs++;
	print_line(vformat("[DoctestRunner] - %s finished tests", p_node->get_name()));

	if (number_of_finished_test_runs == get_child_count()) {
		all_test_runners_finished();
	}
}

void DoctestRunner::all_test_runners_finished() {
	GD_LOCAL_PTR(scene_tree, get_tree());
	if (return_code != 0) {
		print_error("[DoctestRunner] - Error: Doctest unit tests failed, see output for details.");
	}
	print_line(vformat("[DoctestRunner] - All tests finished"));
	scene_tree->quit(return_code);
}
