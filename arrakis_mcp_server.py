#!/usr/bin/env python3
"""
Arrakis MCP Server - Model Context Protocol server for Arrakis VM sandboxes.

This module implements an MCP server that exposes Arrakis VM sandbox functionality
to LLMs through the Model Context Protocol (MCP).
"""

import os
import sys
import argparse
import json
import logging

# Import MCP SDK
from mcp.server.fastmcp import FastMCP

# Import py_arrakis functionality
from py_arrakis.sandbox import Sandbox
from py_arrakis.sandbox_manager import SandboxManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("arrakis-mcp")

# Initialize FastMCP server
mcp = FastMCP("arrakis")

# Default Arrakis server URL
DEFAULT_ARRAKIS_URL = "http://localhost:7000"
# Will be set in main.
sandbox_manager = None

@mcp.resource("arrakis://vms")
def get_vms() -> str:
    """List all available VMs."""
    try:
        vms = sandbox_manager.list_all()
        vm_info = [vm.info() for vm in vms]
        return json.dumps(vm_info, indent=2)
    except Exception as e:
        return f"Error listing VMs: {str(e)}"


@mcp.resource("arrakis://vm/{vm_name}")
def get_vm_info(vm_name: str) -> str:
    """Get information about a specific VM."""
    try:
        sandbox = Sandbox(sandbox_manager._api, vm_name)
        return json.dumps(sandbox.info(), indent=2)
    except Exception as e:
        return f"Error retrieving VM information: {str(e)}"

# Define MCP tools


@mcp.tool()
def start_sandbox(name: str) -> str:
    """
    Start a new sandbox VM.

    Args:
        name: Name to give to the new VM.

    Returns:
        Information about the created VM.
    """
    try:
        sandbox = sandbox_manager.start_sandbox(name)
        return json.dumps(sandbox.info(), indent=2)
    except Exception as e:
        return f"Error starting sandbox: {str(e)}"


@mcp.tool()
def restore_snapshot(vm_name: str, snapshot_id: str) -> str:
    """
    Restore a VM from a snapshot.

    Args:
        vm_name: Name to give to the restored VM.
        snapshot_id: ID of the snapshot to restore from.

    Returns:
        Information about the restored VM.
    """
    try:
        sandbox = sandbox_manager.restore(vm_name, snapshot_id)
        return json.dumps(sandbox.info(), indent=2)
    except Exception as e:
        return f"Error restoring snapshot: {str(e)}"


@mcp.tool()
def snapshot(vm_name: str, snapshot_id: str = "") -> str:
    """
    Create a snapshot of a VM.

    Args:
        vm_name: Name of the VM to snapshot.
        snapshot_id: Optional ID for the snapshot. If not provided, one will be generated.

    Returns:
        ID of the created snapshot.
    """
    try:
        sandbox = Sandbox(sandbox_manager._api, vm_name)
        result = sandbox.snapshot(snapshot_id)
        return f"Created snapshot with ID: {result}"
    except Exception as e:
        return f"Error creating snapshot: {str(e)}"


@mcp.tool()
def run_command(vm_name: str, cmd: str) -> str:
    """
    Run a command in a VM.

    Args:
        vm_name: Name of the VM to run the command in.
        cmd: Command to execute.

    Returns:
        Command output and/or error.
    """
    try:
        sandbox = Sandbox(sandbox_manager._api, vm_name)
        result = sandbox.run_cmd(cmd)
        output = result.get("output", "")
        error = result.get("error", "")

        if error:
            return f"Command output:\n{output}\n\nError:\n{error}"
        return f"Command output:\n{output}"
    except Exception as e:
        return f"Error running command: {str(e)}"


@mcp.tool()
def upload_file(vm_name: str, path: str, content: str) -> str:
    """
    Upload a file to a VM.

    Args:
        vm_name: Name of the VM to upload to.
        path: Destination path in the VM.
        content: Content of the file.

    Returns:
        Success/failure message.
    """
    try:
        sandbox = Sandbox(sandbox_manager._api, vm_name)
        sandbox.upload_files([{"path": path, "content": content}])
        return f"Successfully uploaded file to {path}"
    except Exception as e:
        return f"Error uploading file: {str(e)}"


@mcp.tool()
def download_file(vm_name: str, path: str) -> str:
    """
    Download a file from a VM.

    Args:
        vm_name: Name of the VM to download from.
        path: Path of the file to download.

    Returns:
        Content of the file or error message.
    """
    try:
        sandbox = Sandbox(sandbox_manager._api, vm_name)
        result = sandbox.download_files([path])

        if not result:
            return f"No file found at path: {path}"

        file_data = result[0]
        if "error" in file_data and file_data["error"]:
            return f"Error downloading file: {file_data['error']}"

        return f"File content:\n{file_data.get('content', '')}"
    except Exception as e:
        return f"Error downloading file: {str(e)}"


@mcp.tool()
def destroy_vm(vm_name: str) -> str:
    """
    Destroy a VM.

    Args:
        vm_name: Name of the VM to destroy.

    Returns:
        Success/failure message.
    """
    try:
        sandbox = Sandbox(sandbox_manager._api, vm_name)
        sandbox.destroy()
        return f"Successfully destroyed VM {vm_name}"
    except Exception as e:
        return f"Error destroying VM: {str(e)}"


@mcp.tool()
def destroy_all_vms() -> str:
    """
    Destroy all VMs.

    Returns:
        Success/failure message.
    """
    try:
        sandbox_manager.destroy_all()
        return "Successfully destroyed all VMs"
    except Exception as e:
        return f"Error destroying VMs: {str(e)}"


@mcp.tool()
def update_vm_state(vm_name: str, status: str) -> str:
    """
    Update the state of a VM.

    Args:
        vm_name: Name of the VM to update.
        status: New state for the VM. Must be either 'stopped' or 'paused'.

    Returns:
        Success/failure message.
    """
    try:
        sandbox = Sandbox(sandbox_manager._api, vm_name)
        sandbox.update_state(status)
        return f"Successfully updated VM {vm_name} state to {status}"
    except Exception as e:
        return f"Error updating VM state: {str(e)}"


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Arrakis MCP Server")
    parser.add_argument(
        "--arrakis-url",
        default=DEFAULT_ARRAKIS_URL,
        help=f"URL of the Arrakis server (default: {DEFAULT_ARRAKIS_URL})"
    )
    args = parser.parse_args()
    sandbox_manager = SandboxManager(args.arrakis_url)
    try:
        logger.info("Starting Arrakis MCP Server...")
        # Run the MCP server with stdio transport (default for Claude Desktop)
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Server shutting down...")
    except Exception as e:
        logger.error(f"Error running server: {e}")
        sys.exit(1)
