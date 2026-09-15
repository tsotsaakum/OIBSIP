<?php
/**
 * Load OPENWEATHERMAP_API_KEY from the project .env (never send the key to the browser).
 */
function lentswe_load_env(): void
{
    $path = dirname(__DIR__) . DIRECTORY_SEPARATOR . '.env';
    if (!is_readable($path)) {
        return;
    }
    foreach (file($path, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES) as $line) {
        $line = trim($line);
        if ($line === '' || str_starts_with($line, '#')) {
            continue;
        }
        if (!str_contains($line, '=')) {
            continue;
        }
        [$name, $value] = explode('=', $line, 2);
        $name = trim($name);
        $value = trim($value, " \t\"'");
        if ($name !== '') {
            putenv("$name=$value");
            $_ENV[$name] = $value;
        }
    }
}

function lentswe_api_key(): string
{
    lentswe_load_env();
    $key = trim((string) (getenv('OPENWEATHERMAP_API_KEY') ?: getenv('OPENWEATHER_API_KEY') ?: ''));
    if (in_array(strtolower($key), ['', 'your_key_here', 'changeme', 'none'], true)) {
        return '';
    }
    return $key;
}
