{
  description = "harus-skills development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    { nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            nodejs_22 # prettier, markdownlint-cli2 via npm
            taplo # TOML formatter
            shfmt # shell script formatter
            ruff # Python linter/formatter
            uv # Python package manager
          ];

          shellHook = ''
            if [ ! -d node_modules ]; then
              echo "Installing npm dev tools..."
              npm install --silent
            fi
            export PATH="$PWD/node_modules/.bin:$PATH"
          '';
        };
      }
    );
}
