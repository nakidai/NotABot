FROM archlinux:base
WORKDIR /app
RUN pacman --noconfirm -Syu \
    && pacman --noconfirm -S texlive-basic texlive-latex texlive-latexextra python python-pip \
    && rm -rf /var/cache/pacman/
COPY . .
RUN python -m venv venv \
    && source venv/bin/activate \
    && pip install . \
    && pip cache purge
CMD source venv/bin/activate \
    && notabot $(cat /run/secrets/notabot-token)
