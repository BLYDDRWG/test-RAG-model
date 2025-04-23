#!/usr/bin/env python
"""
Database Management Service Entry Point
"""
import sys
import json
import os
from database_mgmt import store_document_chunks, store_document_chunks_batch

def print_help():
    print("Database Management Service")
    print("Usage:")
    print("  store-chunks <json_file> [--batch-size SIZE]  - Store document chunks from JSON file")
    print("  help                                          - Show this help message")

def main():
    if len(sys.argv) < 2 or sys.argv[1] == "help":
        print_help()
        return
    
    command = sys.argv[1]
    
    if command == "store-chunks":
        if len(sys.argv) < 3:
            print("Error: Missing JSON file path")
            return
        
        json_file = sys.argv[2]
        batch_size = 100  # Default batch size
        
        # Parse optional arguments
        for i in range(3, len(sys.argv)):
            if sys.argv[i] == "--batch-size" and i+1 < len(sys.argv):
                batch_size = int(sys.argv[i+1])
        
        try:
            with open(json_file, 'r') as f:
                chunks = json.load(f)
            
            print(f"Processing {len(chunks)} chunks with batch size {batch_size}")
            if len(chunks) > 50:  # Use batch processing for larger sets
                result = store_document_chunks_batch(chunks, batch_size=batch_size)
            else:
                result = store_document_chunks(chunks)
                
            print(f"Successfully processed {result} chunks")
            
        except FileNotFoundError:
            print(f"Error: JSON file not found: {json_file}")
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in file: {json_file}")
        except Exception as e:
            print(f"Error processing chunks: {e}")
    else:
        print(f"Unknown command: {command}")
        print_help()

if __name__ == "__main__":
    import sys
    import time
    
    # If argument is 'serve', start a server loop
    if len(sys.argv) > 1 and sys.argv[1] == 'serve':
        print("Starting Database Management Service in server mode...")
        while True:
            time.sleep(10)
            print("Database Management Service is running...")
    else:
        # Original behavior
        main()