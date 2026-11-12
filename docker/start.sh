#!/bin/sh
# Trivi'Hackathon 2026: how docker compose starts Odoo (see docker-compose.yml).
# 1. installs every trivia_* module on the first start, and updates them when their files changed since the
#    last update, e.g. after a `git pull` (TRIVIA_UPDATE=force: always update);
# 2. runs Odoo, unless TRIVIA_STOP_AFTER_INIT is set (make init, make update: the errors show in the terminal).
# A failed installation or update stops the container: `docker compose logs odoo` shows why.
set -e
cd /mnt/extra-addons

# no trivia_* module on a branch without the challenges: an empty database, with the base module only
modules=$(for manifest in trivia_*/__manifest__.py; do [ -f "$manifest" ] && dirname "$manifest"; done | paste -s -d, -)
stamp=/var/lib/odoo/trivia_modules.md5
if [ -n "$modules" ]; then
    checksum=$(find trivia_* -type f ! -name '*.pyc' -print0 | sort -z | xargs -0 md5sum | md5sum | cut -d' ' -f1)
else
    checksum=no-module
fi

if [ "$TRIVIA_UPDATE" = force ] || [ "$checksum" != "$(cat "$stamp" 2>/dev/null)" ]; then
    if [ -n "$modules" ]; then
        echo "Trivi'Hackathon: installing / updating $modules"
        # -i installs the modules not installed yet (first start), -u updates the others
        /entrypoint.sh odoo -i "$modules" -u "$modules" --stop-after-init
    else
        echo "Trivi'Hackathon: no trivia_* module yet, creating the database"
        /entrypoint.sh odoo -i base --stop-after-init
    fi
    echo "$checksum" > "$stamp"
fi

if [ -n "$TRIVIA_STOP_AFTER_INIT" ]; then
    exit 0
fi
case " $* " in
    *" --stop-after-init "*) exit 0 ;;
esac
exec /entrypoint.sh odoo "$@"
