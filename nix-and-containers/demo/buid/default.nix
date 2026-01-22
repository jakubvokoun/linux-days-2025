{ pkgs ? import <nixpkgs> { } }:

let
  webServer = pkgs.writeShellScriptBin "web-server" ''
    #!${pkgs.bash}/bin/bash
    mkdir /tmp
    echo "<h1>Hello Linux Days 2025!</h1>" > /tmp/index.html
    echo "Starting simple web server on port 8080..."
    ${pkgs.python3}/bin/python3 -m http.server 8080 --directory /tmp
  '';

  environment = pkgs.buildEnv {
    name = "web-server-env";
    paths = [ pkgs.python3 pkgs.bash pkgs.coreutils webServer ];
  };

in pkgs.dockerTools.buildImage {
  name = "nix-web-server";
  tag = "latest";
  copyToRoot = environment;
  config = {
    Cmd = [ "${webServer}/bin/web-server" ];
    ExposedPorts = { "8080/tcp" = { }; };
    WorkingDir = "/";
    Env = [ "PATH=${environment}/bin" "PYTHONUNBUFFERED=1" ];
  };
}
