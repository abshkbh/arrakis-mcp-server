# Arrakis MCP Server

A Model Context Protocol (MCP) server that exposes [Arrakis](https://github.com/abshkbh/arrakis) VM sandbox functionality to Large Language Models.

## Setup

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/abshkbh/arrakis-mcp-server.git
   cd arrakis-mcp-server
   ```

2. Configure your LLM tool to use the Arrakis MCP server by adding the following to your MCP configuration:

   ```json
   "mcpServers": {
       "arrakis": {
           "command": "<path-to-uv>",
           "args": [
               "--directory",
               "<path-to-repo>",
               "run",
               "arrakis_mcp_server.py"
           ]
       }
   }
   ```

## API

The Arrakis MCP Server exposes the following MCP resources and tools:

### Resources

- `arrakis://vms` - List all available VMs
- `arrakis://vm/{vm_name}` - Get information about a specific VM

### Tools

- `start_sandbox` - Start a new VM sandbox
- `restore_snapshot` - Restore a VM from a snapshot
- `snapshot` - Create a snapshot of a VM
- `run_command` - Run a command in a VM
- `upload_file` - Upload a file to a VM
- `download_file` - Download a file from a VM
- `destroy_vm` - Destroy a specific VM
- `destroy_all_vms` - Destroy all VMs
- `update_vm_state` - Update the state of a VM (pause/stop)

## License

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
