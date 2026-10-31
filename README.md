# Retro PC — Blender project

Исходники процедурной модели ретро-системного блока для Blender.

## Генератор

Файл `blender/create_pc.py` создаёт геометрию корпуса и деталей, делает UV-развёртку через Smart UV Project, запекает материалы в один цветовой атлас 4096×4096 и экспортирует GLB, PNG и BLEND.

## Запуск

1. Открой Blender 3.6 или новее.
2. Перейди во вкладку Scripting.
3. Открой `blender/create_pc.py`.
4. Нажми Run Script.

Результат: `retro_pc_single_atlas.glb`, `retro_pc_single_texture_atlas.png` и `retro_pc_single_atlas.blend` в папке проекта.

**Примечание:** в этом коммите находятся исходный скрипт и документация; готовые бинарные экспорты появятся после запуска скрипта в Blender.
