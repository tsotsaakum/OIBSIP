<?php
declare(strict_types=1);

require __DIR__ . '/config.php';

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

function fail(int $status, string $message): never
{
    http_response_code($status);
    echo json_encode(['ok' => false, 'error' => $message], JSON_UNESCAPED_UNICODE);
    exit;
}

function http_get(string $url): array
{
    $ctx = stream_context_create([
        'http' => ['timeout' => 8, 'ignore_errors' => true, 'header' => "User-Agent: LentsweWeather/1.0\r\n"],
        'ssl' => ['verify_peer' => true, 'verify_peer_name' => true],
    ]);
    $body = @file_get_contents($url, false, $ctx);
    if ($body === false) {
        fail(502, 'Could not reach the weather service.');
    }
    $data = json_decode($body, true);
    return is_array($data) ? $data : [];
}

function looks_like_zip(string $q): bool
{
    return (bool) preg_match('/^(?:\d{5}(?:-\d{4})?|\d{4,10}\s*,\s*[A-Za-z]{2})$/', $q);
}

function query_params(string $q, string $key): string
{
    $base = ['appid' => $key, 'units' => 'metric'];
    if (looks_like_zip($q)) {
        $zip = str_replace(' ', '', $q);
        $base['zip'] = str_contains($zip, ',') ? $zip : ($zip . ',US');
    } else {
        $base['q'] = $q;
    }
    return http_build_query($base);
}

function uv_from_icon(string $icon): float
{
    $map = ['01' => 8.0, '02' => 5.5, '03' => 4.0, '04' => 3.0, '09' => 2.0, '10' => 2.5, '11' => 2.0, '13' => 3.5, '50' => 2.0];
    return $map[substr($icon, 0, 2)] ?? 4.0;
}

function demo_bundle(string $q): array
{
    $seed = hexdec(substr(hash('sha256', strtolower($q)), 0, 8));
    $base = 8 + ($seed % 22);
    $conditions = [
        ['Clear sky', '01d'], ['Few clouds', '02d'], ['Light rain', '10d'],
        ['Broken clouds', '04d'], ['Mist', '50d'], ['Thunderstorm', '11d'],
    ];
    [$desc, $icon] = $conditions[$seed % count($conditions)];
    $now = time();
    $hourly = [];
    for ($h = 0; $h < 6; $h++) {
        $hourly[] = [
            'epoch' => $now + $h * 3600,
            'temp_c' => round($base + sin($h / 2) * 2, 1),
            'description' => $desc,
            'icon' => $icon,
            'pop' => min(0.8, ($seed % 10) / 30 + $h * 0.04),
        ];
    }
    $daily = [];
    $days = ['Today', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    for ($d = 0; $d < 5; $d++) {
        [$dDesc, $dIcon] = $conditions[($seed + $d) % count($conditions)];
        $daily[] = [
            'date_label' => $d === 0 ? 'Today' : date('l', $now + $d * 86400),
            'min_c' => $base - 4,
            'max_c' => $base + 4,
            'description' => $dDesc,
            'icon' => $dIcon,
            'night_icon' => str_replace('d', 'n', $dIcon),
            'pop' => min(0.7, 0.1 + $d * 0.05),
        ];
    }
    return [
        'ok' => true,
        'demo' => true,
        'current' => [
            'place' => ucwords($q),
            'description' => $desc,
            'icon' => $icon,
            'temp_c' => (float) $base,
            'feels_like_c' => (float) ($base - 1),
            'humidity' => 35 + ($seed % 50),
            'wind_mps' => 1.5 + ($seed % 80) / 10,
            'pressure_hpa' => 1000 + ($seed % 31),
            'uv_index' => uv_from_icon($icon),
            'timezone_offset' => 0,
            'sunrise_epoch' => $now - 3600 * 4,
            'sunset_epoch' => $now + 3600 * 6,
            'min_c' => $base - 5,
            'max_c' => $base + 4,
        ],
        'hourly' => $hourly,
        'daily' => $daily,
    ];
}

if (isset($_GET['ip'])) {
    $info = http_get('https://ipinfo.io/json');
    $city = trim((string) ($info['city'] ?? ''));
    $country = trim((string) ($info['country'] ?? ''));
    echo json_encode([
        'ok' => true,
        'city' => $city && $country ? "$city,$country" : ($city ?: null),
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

$q = trim((string) ($_GET['q'] ?? ''));
if ($q === '') {
    fail(400, 'Please enter a city name or ZIP code.');
}

$key = lentswe_api_key();
if ($key === '') {
    echo json_encode(demo_bundle($q), JSON_UNESCAPED_UNICODE);
    exit;
}

$qs = query_params($q, $key);
$currentRaw = http_get('https://api.openweathermap.org/data/2.5/weather?' . $qs);
if ((int) ($currentRaw['cod'] ?? 200) === 401) {
    fail(401, 'The OpenWeatherMap API key is invalid.');
}
if ((int) ($currentRaw['cod'] ?? 200) === 404) {
    fail(404, 'No weather found for "' . $q . '". Check the spelling.');
}
if ((int) ($currentRaw['cod'] ?? 200) >= 400) {
    fail(502, (string) ($currentRaw['message'] ?? 'Weather request failed.'));
}

$forecastRaw = http_get('https://api.openweathermap.org/data/2.5/forecast?' . $qs);
$weather = ($currentRaw['weather'][0] ?? []);
$main = $currentRaw['main'] ?? [];
$wind = $currentRaw['wind'] ?? [];
$sys = $currentRaw['sys'] ?? [];
$icon = (string) ($weather['icon'] ?? '01d');
$now = time();
$offset = (int) ($currentRaw['timezone'] ?? 0);

$list = $forecastRaw['list'] ?? [];
$hourly = [];
for ($h = 0; $h < 6; $h++) {
    $target = $now + $h * 3600;
    $pick = $list[0] ?? null;
    foreach ($list as $item) {
        if ((int) ($item['dt'] ?? 0) >= $target) {
            $pick = $item;
            break;
        }
    }
    $iw = ($pick['weather'][0] ?? []);
    $hourly[] = [
        'epoch' => $target,
        'temp_c' => $h === 0 ? (float) ($main['temp'] ?? 0) : (float) (($pick['main']['temp'] ?? $main['temp']) ?? 0),
        'description' => ucfirst((string) ($iw['description'] ?? $weather['description'] ?? '')),
        'icon' => (string) ($iw['icon'] ?? $icon),
        'pop' => (float) ($pick['pop'] ?? 0),
    ];
}

$buckets = [];
foreach ($list as $item) {
    $local = (int) ($item['dt'] ?? 0) + $offset;
    $day = gmdate('Y-m-d', $local);
    $buckets[$day][] = $item;
}
$daily = [];
foreach (array_slice($buckets, 0, 5, true) as $day => $items) {
    $temps = array_map(fn ($i) => (float) ($i['main']['temp'] ?? 0), $items);
    $pops = array_map(fn ($i) => (float) ($i['pop'] ?? 0), $items);
    $mid = $items[0];
    foreach ($items as $item) {
        $hour = (int) gmdate('G', (int) $item['dt'] + $offset);
        $best = (int) gmdate('G', (int) $mid['dt'] + $offset);
        if (abs($hour - 12) < abs($best - 12)) {
            $mid = $item;
        }
    }
    $night = $items[array_key_last($items)];
    $mw = $mid['weather'][0] ?? [];
    $nw = $night['weather'][0] ?? [];
    $label = (gmdate('Y-m-d', $now + $offset) === $day) ? 'Today' : gmdate('l', strtotime($day . ' UTC'));
    $daily[] = [
        'date_label' => $label,
        'min_c' => $temps ? min($temps) : 0,
        'max_c' => $temps ? max($temps) : 0,
        'description' => ucfirst((string) ($mw['description'] ?? '')),
        'icon' => (string) ($mw['icon'] ?? '01d'),
        'night_icon' => (string) ($nw['icon'] ?? '01n'),
        'pop' => $pops ? max($pops) : 0,
    ];
}

$place = trim(($currentRaw['name'] ?? 'Unknown') . ', ' . ($sys['country'] ?? ''), ' ,');

echo json_encode([
    'ok' => true,
    'demo' => false,
    'current' => [
        'place' => $place,
        'description' => ucfirst((string) ($weather['description'] ?? '')),
        'icon' => $icon,
        'temp_c' => (float) ($main['temp'] ?? 0),
        'feels_like_c' => (float) ($main['feels_like'] ?? $main['temp'] ?? 0),
        'humidity' => (int) ($main['humidity'] ?? 0),
        'wind_mps' => (float) ($wind['speed'] ?? 0),
        'pressure_hpa' => (int) ($main['pressure'] ?? 0),
        'uv_index' => uv_from_icon($icon),
        'timezone_offset' => $offset,
        'sunrise_epoch' => (int) ($sys['sunrise'] ?? 0),
        'sunset_epoch' => (int) ($sys['sunset'] ?? 0),
        'min_c' => (float) ($main['temp_min'] ?? $main['temp'] ?? 0),
        'max_c' => (float) ($main['temp_max'] ?? $main['temp'] ?? 0),
    ],
    'hourly' => $hourly,
    'daily' => $daily,
], JSON_UNESCAPED_UNICODE);
