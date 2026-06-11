while ($true) {
    Write-Host "Realizando commit automático de control de versiones..." -ForegroundColor Cyan
    git add .
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    git commit -m "Autosave programado: $timestamp"
    Write-Host "Guardado completado exitosamente a las $timestamp." -ForegroundColor Green
    Write-Host "Esperando 1 hora (3600 segundos) para el próximo respaldo..."
    Start-Sleep -Seconds 3600
}
