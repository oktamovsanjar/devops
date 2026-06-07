#!/usr/bin/env bash
# ============================================================
# DevOps Bootcamp — Terminal Activity Logger
# Har interaktiv buyruqni timestamp + cwd + exit-code bilan yozadi.
# .bashrc ichida `source` qilinadi (installer buni avtomatik qiladi).
# Bu — real DevOps'dagi "audit logging" texnikasining kichik versiyasi.
# ============================================================

export DEVOPS_HOME="${DEVOPS_HOME:-$HOME/devops}"
export DEVOPS_LOG_DIR="$DEVOPS_HOME/logs/activity"
mkdir -p "$DEVOPS_LOG_DIR" 2>/dev/null

# Har yangi sessiya boshlanganda bir marta yoziladi
if [ -z "$DEVOPS_SESSION_STARTED" ]; then
  export DEVOPS_SESSION_STARTED=1
  printf '%s | SESSION_START | tty=%s\n' \
    "$(date '+%Y-%m-%d %H:%M:%S')" "$(tty 2>/dev/null || echo '?')" \
    >> "$DEVOPS_LOG_DIR/sessions-$(date +%F).log"
fi

# Har buyruqdan keyin ishlaydi (PROMPT_COMMAND orqali)
_devops_log_cmd() {
  local ec=$?                      # oldingi buyruqning exit-code'i (BIRINCHI qator bo'lishi shart)
  local last
  last=$(history 1 2>/dev/null | sed 's/^ *[0-9]\+ *//')
  [ -z "$last" ] && return
  [ "$last" = "$_DEVOPS_LAST_CMD" ] && return   # bir xil buyruqni takror yozmaslik
  _DEVOPS_LAST_CMD="$last"
  printf '%s | ec=%s | %s | %s\n' \
    "$(date '+%Y-%m-%d %H:%M:%S')" "$ec" "$PWD" "$last" \
    >> "$DEVOPS_LOG_DIR/commands-$(date +%F).log"
}

# PROMPT_COMMAND'ga bir marta qo'shamiz (takror qo'shilmaslik tekshiruvi bilan)
case "$PROMPT_COMMAND" in
  *_devops_log_cmd*) ;;
  *) PROMPT_COMMAND="_devops_log_cmd${PROMPT_COMMAND:+; $PROMPT_COMMAND}" ;;
esac
