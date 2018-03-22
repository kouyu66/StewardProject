import os

def get_current_node_info():
    list_pci_commamd = "lspci | grep 'Non-Volatile'"
    nvme_pci_device = steward_lib.linux_command_output_to_list(list_pci_command)
    return nvme_pci_device

print(get_current_node_info())