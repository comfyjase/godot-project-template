#pragma once

#define DOCTEST_RUNNER_NODE_DECLARE(p_class) /****************************************************************************************/ \
    namespace godot {                                                                                                                   \
    class GDExtensionCPPExampleDoctestNode : public Node {                                                                              \
        GDCLASS(GDExtensionCPPExampleDoctestNode, Node);                                                                                \
                                                                                                                                        \
    protected:                                                                                                                          \
        static void _bind_methods();                                                                                                    \
                                                                                                                                        \
    public:                                                                                                                             \
        int doctest_runner_main();                                                                                                      \
        void run_tests();                                                                                                               \
    };                                                                                                                                  \
    }

#define DOCTEST_RUNNER_MAIN_FUNC_IMPLEMENT(p_class) /*********************************************************************************/ \
    int p_class::doctest_runner_main() {                                                                                                \
        PackedStringArray cmd_line_args = OS::get_singleton()->get_cmdline_args();                                                      \
        LocalVector<String> test_args;                                                                                                  \
        for (const String &s : cmd_line_args) {                                                                                         \
            test_args.push_back(s);                                                                                                     \
        }                                                                                                                               \
        doctest::Context context;                                                                                                       \
        if (test_args.size() > 0) {                                                                                                     \
            /** Convert Godot command line arguments back to standard arguments. */                                                     \
            char **doctest_args = new char *[test_args.size()];                                                                         \
            for (uint32_t x = 0; x < test_args.size(); x++) {                                                                           \
                /** Operation to convert Godot string to non wchar string.*/                                                            \
                CharString cs = test_args[x].utf8();                                                                                    \
                const char *str = cs.get_data();                                                                                        \
                /** Allocate the string copy. */                                                                                        \
                doctest_args[x] = new char[strlen(str) + 1];                                                                            \
                /** Copy this into memory. */                                                                                           \
                memcpy(doctest_args[x], str, strlen(str) + 1);                                                                          \
            }                                                                                                                           \
            context.applyCommandLine(test_args.size(), doctest_args);                                                                   \
            for (uint32_t x = 0; x < test_args.size(); x++) {                                                                           \
                delete[] doctest_args[x];                                                                                               \
            }                                                                                                                           \
            delete[] doctest_args;                                                                                                      \
        }                                                                                                                               \
        int result = context.run();                                                                                                     \
        if (context.shouldExit()) {                                                                                                     \
            return result;                                                                                                              \
        }                                                                                                                               \
        return result;                                                                                                                  \
    }                                                                                                                                   \
    void p_class::run_tests() {                                                                                                         \
        int test_results = doctest_runner_main();                                                                                       \
        emit_signal("tests_finished", this, test_results);                                                                              \
    }

#define DOCTEST_RUNNER_NODE_IMPLEMENT(p_class) /**************************************************************************************/ \
    using namespace godot;                                                                                                              \
    void p_class::_bind_methods() {                                                                                                     \
        ClassDB::bind_method(D_METHOD("run_tests"), &p_class::run_tests);                                                               \
        ADD_SIGNAL(MethodInfo("tests_finished", PropertyInfo(Variant::OBJECT, "p_node"), PropertyInfo(Variant::INT, "p_return_code"))); \
    }                                                                                                                                   \
    DOCTEST_RUNNER_MAIN_FUNC_IMPLEMENT(p_class);
