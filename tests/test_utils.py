from unittest.mock import patch, PropertyMock, MagicMock

from pytest import mark

from dcspy import utils


@mark.parametrize('online_tag, result', [('1.1.1', (True, '1.1.1', 'github.com', '09 August 2021', True)),
                                         ('3.2.1', (False, '3.2.1', 'github.com', '09 August 2021', True))])
def test_check_ver_is_possible(online_tag, result):
    with patch.object(utils, 'get') as response_get:
        type(response_get.return_value).ok = PropertyMock(return_value=True)
        type(response_get.return_value).json = MagicMock(return_value={'tag_name': online_tag, 'prerelease': True,
                                                                       'assets': [{'browser_download_url': 'github.com'}],
                                                                       'published_at': '2021-08-09T16:41:51Z'})
        assert utils.check_ver_at_github(repo='fake1/package1', current_ver='1.1.1') == result


def test_check_ver_can_not_check():
    with patch.object(utils, 'get') as response_get:
        type(response_get.return_value).ok = PropertyMock(return_value=False)
        assert utils.check_ver_at_github(repo='fake2/package2', current_ver='2.2.2') == (False, '', '', '', False)


def test_check_ver_exception():
    with patch.object(utils, 'get', side_effect=Exception('Connection error')):
        assert utils.check_ver_at_github(repo='fake3/package3', current_ver='3.3.3') == (False, '', '', '', False)


@mark.parametrize('response, result', [(False, False), (True, True)])
def test_download_file(response, result, tmp_path):
    dl_file = str(tmp_path / 'tmp.txt')
    with patch.object(utils, 'get') as response_get:
        type(response_get.return_value).ok = PropertyMock(return_value=response)
        type(response_get.return_value).iter_content = MagicMock(return_value=[b'1', b'0', b'0', b'1'])
        assert utils.download_file('https://test.com', dl_file) is result


def test_proc_is_running():
    assert utils.proc_is_running('python')
    assert not utils.proc_is_running('wrong_python')


def test_dummy_save_load_set_defaults():
    from os import makedirs, remove, rmdir, environ
    makedirs(name='./tmp', exist_ok=True)
    test_tmp_yaml = './tmp/c.yaml'

    utils.save_cfg({'1': 1}, test_tmp_yaml)
    d_cfg = utils.load_cfg(test_tmp_yaml)
    assert d_cfg == {'1': 1}
    d_cfg = utils.set_defaults(d_cfg)
    assert d_cfg == {'keyboard': 'G13', 'dcsbios': f'D:\\Users\\{environ.get("USERNAME", "UNKNOWN")}\\Saved Games\\DCS.openbeta\\Scripts\\DCS-BIOS'}
    with open(test_tmp_yaml, 'w+') as f:
        f.write('')
    d_cfg = utils.load_cfg(test_tmp_yaml)
    assert len(d_cfg) == 0

    remove(test_tmp_yaml)
    rmdir('./tmp/')