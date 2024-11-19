{ pkgs }: {
  runtimePackages = with pkgs; [
    python3
    python3Packages.pip
    gcc
  ];
  buildCommand = ''
    python -m venv /opt/venv
    . /opt/venv/bin/activate
    pip install -r requirements.txt
  '';
  startCommand = "python app.py";
}
