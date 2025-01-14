from pathlib import Path
from typing import List, Tuple, Union
from unittest.mock import patch

from PIL import Image, ImageChops

from dcspy import aircraft
from dcspy.sdk import lcd_sdk

all_plane_list = ['fa18chornet', 'f16c50', 'f15ese', 'ka50', 'ka503', 'mi8mt', 'mi24p', 'ah64dblkii', 'a10c', 'a10c2', 'f14a135gr', 'f14b', 'av8bna']


def set_bios_during_test(aircraft_model: aircraft.BasicAircraft, bios_pairs: List[Tuple[str, Union[str, int]]]) -> None:
    """
    Set BIOS values for a given aircraft model.

    :param aircraft_model:
    :param bios_pairs:
    """
    if aircraft_model.lcd.type.name == 'COLOR':
        with patch.object(lcd_sdk, 'logi_lcd_is_connected', side_effect=[False, True] * len(bios_pairs)), \
                patch.object(lcd_sdk, 'logi_lcd_color_set_background', return_value=True), \
                patch.object(lcd_sdk, 'logi_lcd_update', return_value=True):
            for selector, value in bios_pairs:
                aircraft_model.set_bios(selector, value)
    else:
        with patch.object(lcd_sdk, 'logi_lcd_is_connected', side_effect=[True] * len(bios_pairs)), \
                patch.object(lcd_sdk, 'logi_lcd_mono_set_background', return_value=True), \
                patch.object(lcd_sdk, 'logi_lcd_update', return_value=True):
            for selector, value in bios_pairs:
                aircraft_model.set_bios(selector, value)


def compare_images(img: Image.Image, file_path: Path, precision: int) -> bool:
    """
    Compare generated image with saved file.

    :param img: Generated image
    :param file_path: path to reference image
    :param precision: allowed precision of image differences
    :return: True if images are the same
    """
    ref_img = Image.open(file_path)
    percents, len_diff = assert_bytes(test_bytes=img.tobytes(), ref_bytes=ref_img.tobytes())
    pixel_diff = ImageChops.difference(img, ref_img)

    if percents > precision or len_diff > 0:
        pixel_diff.save(f'{file_path}_diff.png')
        print(f'\nDiff percentage: {percents}%\nDiff len: {len_diff}\nDiff size: {pixel_diff.getbbox()}')
    return all([percents <= precision, not len_diff])


def assert_bytes(test_bytes: bytes, ref_bytes: bytes) -> Tuple[float, int]:
    """
    Compare bytes and return percentage of differences and differences in size.

    :param test_bytes: bytes to compare
    :param ref_bytes: referenced bytes
    :return: tuple with float of percentage and difference in size
    """
    percents = 0
    try:
        for i, b in enumerate(ref_bytes):
            if b != test_bytes[i]:
                percents += 1
    except IndexError:
        pass
    return float(f'{percents / len(ref_bytes) * 100:.2f}'), len(ref_bytes) - len(test_bytes)
