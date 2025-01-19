#!/bin/bash

# Prerequisites:
# - rsync
# - inotify-tools

# Diretório a ser monitorado
DIR_MONITOR="/brln_backup"

# Comando rsync a ser executado quando uma mudança for detectada
RSYNC_CMD='rsync -avz -e "ssh -p 40371" /brln_backup/ root@jv-gtr.ddns.net:/brln_backup/'

# Arquivo de log (opcional)
LOG_FILE="/var/log/brln_backup_monitor.log"

# Função de backup
backup() {
    echo "[$(date)] Mudança detectada. Iniciando backup..." | tee -a "$LOG_FILE"
    eval $RSYNC_CMD >> "$LOG_FILE" 2>&1

    if [ $? -eq 0 ]; then
        echo "[$(date)] Backup realizado com sucesso." | tee -a "$LOG_FILE"
    else
        echo "[$(date)] Erro ao realizar o backup." | tee -a "$LOG_FILE"
    fi
}

# Intervalo mínimo entre backups (em segundos)
MIN_INTERVAL=30
LAST_RUN=0

# Monitorar mudanças no diretório e executar backup
inotifywait -m -r -e modify,create,delete,move "$DIR_MONITOR" | while read path action file; do
    NOW=$(date +%s)
    if (( NOW - LAST_RUN > MIN_INTERVAL )); then
        echo "[$(date)] Mudança detectada em $path$file devido a $action" | tee -a "$LOG_FILE"
        backup
        LAST_RUN=$NOW
    fi
done
