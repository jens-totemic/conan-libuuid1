#include <stdio.h>
#include <stdlib.h>
#include <uuid/uuid.h>

int main() {
    uuid_t uuid;
    uuid_generate_random(uuid);
    uuid_string_t uuidString;
    uuid_unparse(uuid, uuidString);
    return EXIT_SUCCESS;
}
