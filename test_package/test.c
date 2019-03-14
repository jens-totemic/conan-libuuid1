#include <stdio.h>
#include <stdlib.h>
#include <uuid/uuid.h>

int main() {
    uuid_t uuid;
    uuid_generate_random(uuid);
    char uuidString[37]
    uuid_unparse(uuid, uuidString);
    return EXIT_SUCCESS;
}
