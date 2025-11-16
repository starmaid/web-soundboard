let
  pkgs = import <nixpkgs> {};
in pkgs.mkShell {
  packages = with pkgs; [
    (pkgs.python3.withPackages (python-pkgs: [
      python-pkgs.flask
      python-pkgs.playsound
      python-pkgs.pygobject3
      python-pkgs.pydub
      python-pkgs.yt-dlp
      python-pkgs.waitress
      python-pkgs.openai
      python-pkgs.pytaglib
    ]))
    ffmpeg
    yt-dlp
  ];
}