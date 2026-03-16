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
            nodePackages.prettier # JSON/YAML formatter
            taplo # TOML formatter
            shfmt # shell script formatter
            ruff # Python linter/formatter
          ];
        };
      }
    );
}
