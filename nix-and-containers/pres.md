---
marp: true
theme: default
paginate: true
header: 'Nix & kontejnery'
footer: 'Jakub Vokoun | Linux Days 2025'
style: |
  section {
    font-size: 28px;
  }
  h1 {
    font-size: 42px;
  }
  h2 {
    font-size: 36px;
  }
  h3 {
    font-size: 32px;
  }
  pre {
    font-size: 16px;
    line-height: 1.3;
  }
  code {
    font-size: 18px;
  }
  table {
    font-size: 22px;
  }
  ul, ol {
    font-size: 26px;
  }
  blockquote {
    font-size: 24px;
  }
---
# Nix & kontejnery

> Jakub Vokoun
> jakub.vokoun@wftech.cz

---

# `whoami(1)`

- linuxák skoro již 20 let
- "liný DevOpsák, který automatizuje, co potká"

---

# Motivace

- deklarativní spouštění kontejnerů na NixOS
- deklarativní buildy
- deklarativní<sup>1</sup> řešení pro `docker compose`

> <sup>1</sup> Ano, slovo deklarativní tu dnes bude slyšet často

---

# Nix 101

## Nix

- jazyk
- CLI nástroj
- operační systém

---

# Nix 101

## Jazyk Nix

- dynamicky typovaný
- funkcionální
- lazy evaluation
- DSL (Domain Specific Language)

---

# Proč Nix?

## Co znamená "deklarativní"

- **Reprodukovatelnost** - stejný výsledek na každém stroji
- **Immutabilita** - buildy se nemění, jen se vytváří nové
- **Rollback** - jednoduché vrácení na předchozí verzi
- **Izolace** - žádné konflikty závislostí

---

# Kontejnery 101

- Docker
- Podman
- LXC (Linux Containers), Incus
- `systemd-nspawn(1)`

---

# Kontejnery _tradičně_

```sh
docker run image:tag command
```

```sh
docker run --detach image command
```

```sh
docker run --rm --interactive --tty image command
```

---

# Kontejnery _tradičně_

```dockerfile
# Dockerfile
FROM python:3.13
WORKDIR /usr/local/app

# Install the application dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy in the source code
COPY src ./src
EXPOSE 8080

# Setup an app user so the container doesn't run as the root user
RUN useradd app
USER app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

---

# Kontejnery _tradičně_

```sh
docker build -t local/my-python-app .
```

```sh
docker run -p 8080:8080 local/my-python-app:latest
```

---

# Docker vs Nix

| Aspekt | Docker | Nix |
|--------|--------|-----|
| **Reprodukovatelnost** | Závisí na čase buildu | Garantovaná |
| **Velikost image** | Obsahuje OS layer | Jen potřebné závislosti |
| **Cache** | Layer-based | Content-addressed |
| **Rollback** | Ruční tag management | Automatický |
| **Dev prostředí** | Dockerfile + compose | Jedna konfigurace |

---

# Kontejnery _the Nix way_

## Incus - základní konfigurace

```nix
{ config, pkgs, lib, ... }:

{
  virtualisation.incus = {
    enable = true;
    ui = { enable = true; };
  };
  networking.nftables.enable = true;
  users.extraGroups.incus-admin.members = [ "jakub" ];
}
```

```sh
sudo nixos-rebuild --switch
sudo incus admin init --minimal
```

---

# Kontejnery _the Nix way_

## Incus - custom images

```nix
nixosConfigurations = {
  container = inputs.nixpkgs.lib.nixosSystem {
    system = "x86_64-linux";
    modules = [
      "${inputs.nixpkgs}/nixos/modules/virtualisation/lxc-container.nix"
      (
        { pkgs, ... }:
        {
          environment.systemPackages = [ pkgs.vim ];
        }
      )
    ];
  };
};
```

---

# Kontejnery _the Nix way_

## Incus - custom images

```nix
nixosConfigurations = {
  vm = inputs.nixpkgs.lib.nixosSystem {
    system = "x86_64-linux";
    modules = [
      "${inputs.nixpkgs}/nixos/modules/virtualisation/lxd-virtual-machine.nix"
      (
        { pkgs, ... }:
        {
          environment.systemPackages = [ pkgs.vim ];
        }
      )
    ];
  };
};
```

---


# Kontejnery _the Nix way_

## Incus - custom images

```sh
incus image import --alias nixos/custom/vm \
    $(nix build .#nixosConfigurations.vm.config.system.build.metadata --print-out-paths)/tarball/nixos-system-x86_64-linux.tar.xz \
    $(nix build .#nixosConfigurations.vm.config.system.build.qemuImage --print-out-paths)/nixos.qcow2
```

```sh
incus image import --alias nixos/custom/container \
    $(nix build .#nixosConfigurations.container.config.system.build.metadata --print-out-paths)/tarball/nixos-system-x86_64-linux.tar.xz \
    $(nix build .#nixosConfigurations.container.config.system.build.squashfs --print-out-paths)
```

---

# Kontejnery _the Nix way_

## Docker - základní konfigurace

```nix
{ config, pkgs, ... }: {
  virtualisation.docker.enable = true;
  users.extraGroups.docker.members = [ "jakub" ];
}
```

---

# Kontejnery _the Nix way_

## Docker - pokročilá konfigurace

```nix
{ config, pkgs, ... }: {
  virtualisation.docker = {
    enable = true;
    daemon.settings = {
      dns = [ "1.1.1.1" "8.8.8.8" ];
      log-driver = "journald";
      registry-mirrors = [ "https://mirror.gcr.io" ];
      storage-driver = "overlay2";
    };
    rootless = {
      enable = true;
      setSocketVariable = true;
    };
  };
}
```

---

# Kontejnery _the Nix way_

## Podman

```nix
{ config, pkgs, ... }: {
  virtualisation.containers.enable = true;
  virtualisation = {
    podman = {
      enable = true;
      # Docker alias
      dockerCompat = true;
      # Required for `podman-compose`
      defaultNetwork.settings.dns_enabled = true;
    };
  };

  # Additional packages
  environment.systemPackages = with pkgs; [ docker-compose podman-compose ];
}
```

---

# Kontejnery _the Nix way_

## Spuštění kontejneru

```nix
{ config, pkgs, ... }: {
  # Use Podman
  virtualisation.oci-containers.backend = "podman";

  # my-python-app container
  virtualisation.oci-containers.containers = {
    my-python-app = {
      image = "local/my-python-app:latest";
      ports = [ "8080:8080" ];
      volumes = [ ];
      cmd = [ "uvicorn" "app.main:app" "--host" "0.0.0.0" "--port" "8080" ];
    };
  };
}
```

---

# Kontejnery _the Nix way_

## Build

```nix
{ pkgs ? import <nixpkgs> { }
, pkgsLinux ? import <nixpkgs> { system = "x86_64-linux"; } }:

pkgs.dockerTools.buildImage {
  name = "hello-docker";
  config = { Cmd = [ "${pkgsLinux.hello}/bin/hello" ]; };
}
```

---

# Kontejnery _the Nix way_

## Build

```sh
nix-build hello-docker.nix 
/nix/store/15iq02c94d0r3ha2kd7rhz7z8035v8hc-docker-image-hello-docker.tar.gz
```

```sh
tree
.
├── hello-docker.nix
└── result -> /nix/store/15iq02c94d0r3ha2kd7rhz7z8035v8hc-docker-image-hello-docker.tar.gz
```

```sh
docker load < result
```

---

# Kontejnery _the Nix way_

## `compose2nix`

```sh
nix run github:aksiksi/compose2nix -- -h
```

```nix
{ config, pkgs, ... }: {
  # Add `compose2nix` package 
  environment.systemPackages = [ pkgs.compose2nix ];
}
```

---

# Kontejnery _the Nix way_

## `compose2nix`

```sh
compose2nix -project=my-app --inputs=compose.yml --output=compose.nix --runtime=docker --env_files=.env
```

```sh
compose2nix -project=my-app --inputs=compose.yml --output=compose.nix --runtime=podman --env_files=.env
```

---

# Kontejnery _the Nix way_

## `compose2nix` - labely

```yaml
services:
  my-service:
    labels:
      # Enable
      - "compose2nix.settings.autoStart=true"
```

## `compose2nix` - limitace

- nemá 1:1 podporu pro `depends_on`

---

# Demo

## 1. Nix image build - webový server

```sh
nix-build demo/buid/default.nix
docker load < result
docker run -p 8080:8080 nix-web-server:latest
# curl localhost:8080
```

## 2. compose2nix - Gitea + PostgreSQL

```sh
# Ukázka původního compose.yml
# Ukázka vygenerovaného compose.nix
nixos-rebuild switch
systemctl status docker-gitea-server
```

---

# Reference

- https://github.com/the-nix-way/nix-docker-examples/
- https://github.com/aksiksi/compose2nix
