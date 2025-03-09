#include <iostream>
#include <libvbox.h>

int main(void) {
    // taken from the first example: "List Machines"
    // see https://github.com/zrax/libvbox/blob/bf5788fe940a00c0549af8c49929cc7b024eaaf9/README.md
    try
    {
        auto vboxClient = VBox::virtualBoxClient();
        auto vbox = vboxClient->virtualBox();
        auto machines = vbox->machines();
        for (const auto &machine : machines)
            std::wcout << VBox::utf16ToWide(machine->name()) << std::endl;
    }
    catch (const std::exception& ex)
    {
        std::cerr << "Error: " << ex.what();
        return EXIT_FAILURE;
    }
    
    return EXIT_SUCCESS;
}
