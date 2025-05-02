# Safe delete function for Obsidian files and directories
safe_delete() {
  local trash_dir=".trash"
  local current_date=$(date +%Y%m%d%H%M%S)
  
  # Check if .trash directory exists, if not create it
  if [ ! -d "$trash_dir" ]; then
    mkdir -p "$trash_dir"
  fi
  
  for target in "$@"; do
    if [ -e "$target" ]; then
      # Create a unique name with timestamp to avoid conflicts
      local base_name=$(basename "$target")
      local trash_path="$trash_dir/${current_date}_${base_name}"
      
      # Create a log entry
      echo "$(date '+%Y-%m-%d %H:%M:%S') - Moved: $target -> $trash_path" >> "$trash_dir/deletion_log.txt"
      
      # Move the file or directory to trash
      mv "$target" "$trash_path"
      echo "Moved '$target' to trash as '${current_date}_${base_name}'"
    else
      echo "Warning: '$target' does not exist"
    fi
  done
}

# Function to restore files from trash
restore_from_trash() {
  local trash_dir=".trash"
  
  if [ ! -d "$trash_dir" ]; then
    echo "Trash directory does not exist"
    return 1
  fi
  
  # List files in trash with numbers
  local i=1
  local files=()
  echo "Files in trash:"
  for file in "$trash_dir"/*; do
    if [ -e "$file" ] && [ "$file" != "$trash_dir/deletion_log.txt" ]; then
      echo "$i) $(basename "$file")"
      files[$i]="$file"
      ((i++))
    fi
  done
  
  # Ask which file to restore
  echo "Enter the number of the file to restore (or 'q' to quit):"
  read choice
  
  if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -gt 0 ] && [ "$choice" -lt "$i" ]; then
    local file_to_restore="${files[$choice]}"
    local original_name=$(basename "$file_to_restore" | sed 's/^[0-9]\{14\}_//')
    
    # Check if a file with the same name exists
    if [ -e "$original_name" ]; then
      echo "Warning: A file with the name '$original_name' already exists"
      echo "Enter a new name for the restored file (or 'q' to quit):"
      read new_name
      if [ "$new_name" != "q" ]; then
        mv "$file_to_restore" "$new_name"
        echo "Restored as '$new_name'"
      fi
    else
      mv "$file_to_restore" "$original_name"
      echo "Restored '$original_name'"
    fi
  elif [ "$choice" != "q" ]; then
    echo "Invalid choice"
  fi
}

# Prevent the use of rm -rf
rm_rf() {
  echo "Warning: 'rm -rf' is disabled for safety. Use 'rm_obs' instead."
  return 1
}

# Aliases
alias rm_obs='safe_delete'
alias restore='restore_from_trash'
alias rm='rm_obs'  # Replace standard rm with safe_delete
alias 'rm -rf'='rm_rf'  # Prevent rm -rf 