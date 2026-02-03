---
name: mkmr
description: create merge request to mainline branch based on current branch
metadata:
  author: haru
  version: "1.0.0"
allowed-tools: git gh glab
---

1. always ask for user's permission (before execute any task/command)
2. ask user what is the mainline branch, `main` or `develop`
3. check `gh` or `glab` availability; if not, provide instructions to install the specific tool
4. if current branch was mainline branch, gracefully complete here (as no further tasks)
5. check if any more files shall be added to stash and committed
6. use `git` to check the diff between current branch and mainline branch, commit to local stash if necessary
   1. represent the diff with concise and detailed documentation
   2. avoid using emojis
7. push current branch to remote if necessary
8. use `gh` or `glab` to create the merge request
   1. add informative message to the description
   2. with co-authorized information (if you like)
