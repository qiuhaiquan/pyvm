#include "util/bufferedInputStream.hpp"
#include "code/binaryFileParser.hpp"
#include "runtime/interpreter.hpp"
#include "runtime/universe.hpp"
#include "memory/heap.hpp"

int interpreter(char** dir) {
    if (not dir){
        return -1
    }
    Universe::genesis();
    BufferedInputStream stream(argv[1]);
    BinaryFileParser parser(&stream);
    Universe::main_code = parser.parse();
    Universe::heap->gc();

    Interpreter::get_instance()->run(Universe::main_code);

    return 0;
}

