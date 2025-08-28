let
  pkgs = import <nixpkgs> {};
in pkgs.mkShell {
  packages = [
    (pkgs.python3.withPackages (python-pkgs: [
      python-pkgs.pandas
      python-pkgs.requests
      python-pkgs.flask
      python-pkgs.pymongo
      python-pkgs.python-dotenv
      python-pkgs.flask-sqlalchemy
      python-pkgs.flask-mysqldb
      #python-pkgs.jedi-language-server
      python-pkgs.python-lsp-server
      python-pkgs.flask-session
    ]))
    pkgs.ruff
    pkgs.superhtml
    pkgs.vscode-langservers-extracted
    pkgs.typescript-language-server
    pkgs.yaml-language-server
    pkgs.ansible-language-server
    pkgs.marksman
    pkgs.markdown-oxide
  ];
}
