
#  Copyright 2016 by Dai Trying
#
#  This file is part of daixmms2skin.
#
#     daixmms2skin is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     daixmms2skin is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with daixmms2skin.  If not, see <http://www.gnu.org/licenses/>.


import xmmsfun
import math
from PyQt5.Qt import QColor
from PyQt5.QtWidgets import QInputDialog, QFileDialog
from xmmsclient import xmmsvalue
import os
from ConfigParser import SafeConfigParser

if not os.path.isdir(os.path.join(os.path.expanduser('~'), ".config/daixmmsdata")):
    try:
        os.makedirs(os.path.join(os.path.expanduser('~'), ".config/daixmmsdata"))
    except OSError:
        pass


conffile = os.path.join(os.path.expanduser('~'), ".config/daixmmsdata/config.conf")


def set_new_config_file():
    conf_sections1 = ['table_ml_columns_show', 'table_pl_columns_show', 'table_np_columns_show']
    conf_sections2 = ['table_ml_columns_size', 'table_pl_columns_size', 'table_np_columns_size']
    section1_keys = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 'rows']
    section2_keys = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    config = SafeConfigParser()
    for section1 in conf_sections1:
        config.add_section(section1)
        for the_key in section1_keys:
            config.set(section1, str(the_key), (str(True)))
    for section2 in conf_sections2:
        config.add_section(section2)
        for the_key in section2_keys:
            config.set(section2, str(the_key), (str(100)))

    with open(conffile, 'w') as f:
        config.write(f)


if os.path.isfile(conffile):
    pass
else:
    cfile = open(conffile, 'a')
    cfile.close()
    set_new_config_file()


def load_media_to_library(self):
    """
    Load all media entries from medialib to memory [list(My_Library)]
    :param self: calling Object
    :return: None
    """
    media_list = xmmsfun.xmms_get_all_library_list()
    self.tableMediaLibrary.setSortingEnabled(False)
    for item in media_list.value():
        track = clean_track(item)
        self.My_Library.append(track)
        add_row_to_table(self.tableMediaLibrary, track)
    self.tableMediaLibrary.setSortingEnabled(True)


def load_play_lists(self):
    """
    Load all playlists to memory [list(Play_Lists)]
    :param self:
    :return: None
    """
    all_pls = []
    pls = xmmsfun.xmms_get_list_of_play_lists()
    for pl in pls.value():
        if pl.startswith("_") or pl == "Default":
            pass
        else:
            all_pls.append(pl)
    for item in sorted(all_pls, key=lambda s: s.lower()):
        self.combo_pl_names.addItem(item)
        pl_ids = xmmsfun.xmms_get_playlist_entries(item)
        if pl_ids is not False:
            self.Play_Lists.append({"Name": item, "Ids": pl_ids.value()})
    load_pl_entries_table(self)


def load_pl_entries_table(self):
    """
    Load the currently selected playlist to playlist table
    :param self:
    :return: None
    """
    pl = self.combo_pl_names.currentText()
    self.table_pl_entries.setRowCount(0)
    if pl is None or pl is False or pl == "":
        return False
    ml_ids = get_playlist_entries_from_mem(self, pl)
    if ml_ids is not False:
        for this_id in ml_ids:
            track = get_info_by_ml_id(self, this_id)
            add_row_to_table(self.table_pl_entries, track)


def load_now_playing(self):
    """
    Load current playlist to Now Playing table
    :param self:
    :return: None
    """
    npl = xmmsfun.xmms_get_now_playing_entries()
    for np in npl.value():
        track = get_info_by_ml_id(self, np)
        add_row_to_table(self.tableNowPlaying, track)
    current_row = xmmsfun.xmms_get_now_playing_pl_id()
    if current_row is not False and current_row.value()['position'] is not -1:
        highlight_row(self, current_row.value()['position'])


def insert_row_to_table(row, table, data):
    """
    Insert given row to given table with given data
    :param row: int
    :param table: Object
    :param data: item from [list(My_Library]
    :return: None
    """
    table.insertRow(row)
    set_row_to_table(row, table, data)


def set_row_to_table(row, table, data):
    """
    Set data at given row in given table using given data
    :param row: int
    :param table: Object
    :param data: item from [list(My_Library)]
    :return: None
    """
    table.set_row_data(row, data['id'], data['tracknr'], data['album'], data['partofset'], data['title'],
                       data['artist'], data['genre'], data['performer'],
                       data['duration'], data['timesplayed'], data['bitrate'], data['filesize'])


def add_row_to_table(table, data):
    """
    Add row to end of given table with given data
    :param table: Object
    :param data: item from [list(My_Library)]
    :return: None
    """
    row = table.rowCount()
    insert_row_to_table(row, table, data)


def get_playlist_entries_from_mem(self, plist):
    """
    Get details from memory [list(Play_Lists)] for given playlist
    :param self:
    :param plist: str
    :return: list of medialib id's of False on error
    """
    if plist is None or plist is False:
        return False
    my_item = next((item for item in self.Play_Lists if item['Name'] == plist), None)
    if my_item is None:
        return False
    else:
        return my_item['Ids']


def get_info_by_ml_id(self, ml_id):
    """
    Get track information for given medialib id from memory [list(My_Library)]
    :param self:
    :param ml_id: int
    :return: iten from [list(My_Library)] or False on error
    """
    my_item = next((item for item in self.My_Library if item['id'] == ml_id), None)
    if my_item is None:
        return False
    return my_item


# noinspection SpellCheckingInspection
def clean_track(track):
    """
    Clean all track variables for insertion to memory/table from given dict
    :param track: dict
    :return: dict
    """
    try:
        ml_id = track['id']
    except AttributeError:
        ml_id = "Unknown"
    try:
        if track['partofset'] is None:
            pos = 0
        else:
            pos = track['partofset']
    except AttributeError:
        pos = 0
    except KeyError:
        pos = 0
    try:
        if track['tracknr'] is None:
            tracknr = 0
        else:
            tracknr = track['tracknr']
    except AttributeError:
        tracknr = 0
    except KeyError:
        tracknr = 0
    try:
        if track['title'] is None:
            title = "Unknown"
        else:
            title = track['title']
    except AttributeError:
        title = "Unknown"
    except KeyError:
        title = "Unknown"
    try:
        if track['artist'] is None:
            artist = "Unknown"
        else:
            artist = track['artist']
    except AttributeError:
        artist = "Unknown"
    except KeyError:
        artist = "Unknown"
    try:
        if track['album'] is None:
            album = "Unknown"
        else:
            album = track['album']
    except AttributeError:
        album = "Unknown"
    except KeyError:
        album = "Unknown"
    try:
        if track['genre'] is None:
            genre = "Unknown"
        else:
            genre = track['genre']
    except AttributeError:
        genre = "Unknown"
    except KeyError:
        genre = "Unknown"
    try:
        if track['bitrate'] is None:
            bitrate = "Unknown"
        else:
            bitrate = track['bitrate']
    except AttributeError:
        bitrate = "Unknown"
    except KeyError:
        bitrate = "Unknown"
    try:
        if track['performer'] is None:
            album_artist = "Unknown"
        else:
            album_artist = track['performer']
    except AttributeError:
        album_artist = "Unknown"
    except KeyError:
        album_artist = "Unknown"
    try:
        if track['duration'] is None:
            duration = "Unknown"
        else:
            duration = track['duration']
    except AttributeError:
        duration = "Unknown"
    except KeyError:
        duration = "Unknown"
    try:
        if track['timesplayed'] is None:
            times_played = "Unknown"
        else:
            times_played = track['timesplayed']
    except AttributeError:
        times_played = "Unknown"
    except KeyError:
        times_played = "Unknown"
    try:
        if track['size'] is None:
            file_size = "Unknown"
        else:
            file_size = track['size']
    except AttributeError:
        file_size = "Unknown"
    except KeyError:
        file_size = "Unknown"
    new_track = {'id': ml_id, 'title': title, 'artist': artist, 'album': album, 'genre': genre, 'bitrate': bitrate,
                 'performer': album_artist, 'duration': duration, 'timesplayed': times_played, 'filesize': file_size,
                 "tracknr": tracknr, "partofset": pos}
    return new_track


# noinspection SpellCheckingInspection
def clean_track_result(track):
    """
    Clean all track variables for insertion to memory/table from given XmmsResult
    :param track: XmmsResult
    :return: dict
    """
    try:
        ml_id = track.value()['id']
    except AttributeError:
        ml_id = "Unknown"
    try:
        if track.value()['partofset'] is None:
            pos = 0
        else:
            pos = track.value()['partofset']
    except AttributeError:
        pos = 0
    except KeyError:
        pos = 0
    try:
        if track.value()['tracknr'] is None:
            tracknr = 0
        else:
            tracknr = track.value()['tracknr']
    except AttributeError:
        tracknr = 0
    except KeyError:
        tracknr = 0
    try:
        if track.value()['title'] is None:
            title = "Unknown"
        else:
            title = track.value()['title']
    except AttributeError:
        title = "Unknown"
    except KeyError:
        title = "Unknown"
    try:
        if track.value()['artist'] is None:
            artist = "Unknown"
        else:
            artist = track.value()['artist']
    except AttributeError:
        artist = "Unknown"
    except KeyError:
        artist = "Unknown"
    try:
        if track.value()['album'] is None:
            album = "Unknown"
        else:
            album = track.value()['album']
    except AttributeError:
        album = "Unknown"
    except KeyError:
        album = "Unknown"
    try:
        if track.value()['genre'] is None:
            genre = "Unknown"
        else:
            genre = track.value()['genre']
    except AttributeError:
        genre = "Unknown"
    except KeyError:
        genre = "Unknown"
    try:
        if track.value()['bitrate'] is None:
            bitrate = "Unknown"
        else:
            bitrate = track.value()['bitrate']
    except AttributeError:
        bitrate = "Unknown"
    except KeyError:
        bitrate = "Unknown"
    try:
        if track.value()['performer'] is None:
            album_artist = "Unknown"
        else:
            album_artist = track.value()['performer']
    except AttributeError:
        album_artist = "Unknown"
    except KeyError:
        album_artist = "Unknown"
    try:
        if track.value()['duration'] is None:
            duration = "Unknown"
        else:
            duration = track.value()['duration']
    except AttributeError:
        duration = "Unknown"
    except KeyError:
        duration = "Unknown"
    try:
        if track.value()['timesplayed'] is None:
            times_played = "Unknown"
        else:
            times_played = track.value()['timesplayed']
    except AttributeError:
        times_played = "Unknown"
    except KeyError:
        times_played = "Unknown"
    try:
        if track.value()['size'] is None:
            file_size = "Unknown"
        else:
            file_size = track.value()['size']
    except AttributeError:
        file_size = "Unknown"
    except KeyError:
        file_size = "Unknown"
    new_track = {'id': ml_id, 'title': title, 'artist': artist, 'album': album, 'genre': genre, 'bitrate': bitrate,
                 'performer': album_artist, 'duration': duration, 'timesplayed': times_played, 'filesize': file_size,
                 "tracknr": tracknr, "partofset": pos}
    return new_track


def ms_int_to_time(ms):
    """
    Convert time in milliseconds to tuple (minutes, seconds)
    :param ms: int
    :return: tuple
    """
    minutes = ms / 60000
    seconds = (ms % 60000)/1000
    return "%02i:%02i" % (minutes, seconds)


def convert_to_size(size):
    """
    Convert bytes number to Kb/Mb/Gb values
    :param size: int
    :return: formatted string (??.??kb/Mb/Gb)
    """
    if size == 0:
        return '0b'
    size_name = ("b", "Kb", "Mb", "Gb")
    i = int(math.floor(math.log(size, 1024)))
    p = math.pow(1024, i)
    s = round(size/p, 2)
    return '%s %s' % (s, size_name[i])


def playlist_position_change(self, result):
    if result.value()['name'] == "Default":
        if result.value()['position'] < 0:
            if xmmsfun.xmms_next() is False:
                xmmsfun.xmms_stop()
                return False
            else:
                highlight_row(self, result.value()['position']+1)
                return True
        else:
            highlight_row(self, result.value()['position'])
            return True
    else:
        return False


def highlight_current(self):
    pl_row = xmmsfun.xmms_get_now_playing_pl_id()
    highlight_row(self, pl_row.value()['position'])


def highlight_row(self, this_row):
    allrows = self.tableNowPlaying.rowCount()
    for row in xrange(0, allrows):
        self.tableNowPlaying.item(row, 0).setBackground(QColor(255, 255, 255))
        self.tableNowPlaying.item(row, 1).setBackground(QColor(255, 255, 255))
        self.tableNowPlaying.item(row, 2).setBackground(QColor(255, 255, 255))
        self.tableNowPlaying.item(row, 3).setBackground(QColor(255, 255, 255))
        self.tableNowPlaying.item(row, 4).setBackground(QColor(255, 255, 255))
        self.tableNowPlaying.item(row, 5).setBackground(QColor(255, 255, 255))
        self.tableNowPlaying.item(row, 6).setBackground(QColor(255, 255, 255))
        self.tableNowPlaying.item(row, 7).setBackground(QColor(255, 255, 255))
        self.tableNowPlaying.item(row, 8).setBackground(QColor(255, 255, 255))
        self.tableNowPlaying.item(row, 9).setBackground(QColor(255, 255, 255))
        self.tableNowPlaying.item(row, 10).setBackground(QColor(255, 255, 255))
        self.tableNowPlaying.item(row, 11).setBackground(QColor(255, 255, 255))
    if this_row is -1:
        return False
    try:
        self.tableNowPlaying.item(this_row, 0).setBackground(QColor(47, 127, 255))
        self.tableNowPlaying.item(this_row, 1).setBackground(QColor(47, 127, 255))
        self.tableNowPlaying.item(this_row, 2).setBackground(QColor(47, 127, 255))
        self.tableNowPlaying.item(this_row, 3).setBackground(QColor(47, 127, 255))
        self.tableNowPlaying.item(this_row, 4).setBackground(QColor(47, 127, 255))
        self.tableNowPlaying.item(this_row, 5).setBackground(QColor(47, 127, 255))
        self.tableNowPlaying.item(this_row, 6).setBackground(QColor(47, 127, 255))
        self.tableNowPlaying.item(this_row, 7).setBackground(QColor(47, 127, 255))
        self.tableNowPlaying.item(this_row, 8).setBackground(QColor(47, 127, 255))
        self.tableNowPlaying.item(this_row, 9).setBackground(QColor(47, 127, 255))
        self.tableNowPlaying.item(this_row, 10).setBackground(QColor(47, 127, 255))
        self.tableNowPlaying.item(this_row, 11).setBackground(QColor(47, 127, 255))
        return True
    except AttributeError:
        return False


def playlist_changed(self, result):
    # print("Playlist Changed")
    if result.value()["type"] == 0:
        # print("    Add " + str(result.value()))
        if result.value()['name'] == "Default":
            insert_row_to_table(result.value()['position'], self.tableNowPlaying,
                                get_info_by_ml_id(self, result.value()['id']))
        elif result.value()['name'] == self.combo_pl_names.currentText():
            insert_row_to_table(result.value()['position'], self.table_pl_entries,
                                get_info_by_ml_id(self, result.value()['id']))
            add_ml_id_to_playlists(self, result.value()['id'], result.value()['name'])
        else:
            add_ml_id_to_playlists(self, result.value()['id'], result.value()['name'])
    elif result.value()["type"] == 1:
        # print("    Insert " + str(result.value()))
        if result.value()['name'] == "Default":
            insert_row_to_table(result.value()['position'], self.tableNowPlaying,
                                get_info_by_ml_id(self, result.value()['id']))
        elif result.value()['name'] == self.combo_pl_names.currentText():
            insert_row_to_table(result.value()['position'], self.table_pl_entries,
                                get_info_by_ml_id(self, result.value()['id']))
            add_ml_id_to_playlists(self, result.value()['id'], result.value()['name'])
        else:
            add_ml_id_to_playlists(self, result.value()['id'], result.value()['name'])
    elif result.value()["type"] == 2:
        # print("    Shuffle " + str(result.value()))
        if result.value()['name'] == "Default":
            self.tableNowPlaying.setRowCount(0)
            load_now_playing(self)
        elif result.value()['name'] == self.combo_pl_names.currentText():
            self.table_pl_entries.setRowCount(0)
            refresh_playlists(self, result.value()['name'])
            load_pl_entries_table(self)
        else:
            thislist = self.combo_pl_names.currentText()
            refresh_playlists(self, result.value()['name'])
            self.combo_pl_names.setCurrentIndex(self.combo_pl_names.findText(thislist))
    elif result.value()["type"] == 3:
        # print("    Remove" + str(result.value()))
        if result.value()['name'] == "Default":
            self.tableNowPlaying.removeRow(result.value()['position'])
        elif result.value()['name'] == self.combo_pl_names.currentText():
            self.table_pl_entries.removeRow(result.value()['position'])
            remove_position_from_playlists(self, result.value()['position'], result.value()['name'])
        else:
            remove_position_from_playlists(self, result.value()['position'], result.value()['name'])
    elif result.value()["type"] == 4:
        # print("    Clear " + str(result.value()))
        if result.value()['name'] == "Default":
            self.tableNowPlaying.setRowCount(0)
            if xmmsfun.xmms_get_play_status().value() == 1:
                xmmsfun.xmms_stop()
        elif result.value()['name'] == self.combo_pl_names.currentText():
            self.table_pl_entries.setRowCount(0)
            clear_playlist(self, result.value()['name'])
        else:
            clear_playlist(self, result.value()['name'])
    elif result.value()["type"] == 5:
        # print("    Move " + str(result.value()))
        if result.value()['name'] == "Default":
            # print("Default")
            self.tableNowPlaying.removeRow(result.value()['position'])
            insert_row_to_table(result.value()['newposition'], self.tableNowPlaying,
                                get_info_by_ml_id(self, result.value()['id']))
        elif result.value()['name'] == self.combo_pl_names.currentText():
            # print("playlist")
            self.table_pl_entries.removeRow(result.value()['position'])
            insert_row_to_table(result.value()['newposition'], self.table_pl_entries,
                                get_info_by_ml_id(self, result.value()['id']))
            move_position_in_playlists(self, result.value()['name'], result.value()['position'],
                                       result.value()['newposition'])
        else:
            move_position_in_playlists(self, result.value()['name'], result.value()['position'],
                                       result.value()['newposition'])
    elif result.value()["type"] == 6:
        # print("    Sort " + str(result.value()))
        if result.value()['name'] == "Default":
            self.tableNowPlaying.setRowCount(0)
            load_now_playing(self)
        elif result.value()['name'] == self.combo_pl_names.currentText():
            self.table_pl_entries.setRowCount(0)
            refresh_playlists(self, result.value()['name'])
            load_pl_entries_table(self)
        else:
            thislist = self.combo_pl_names.currentText()
            refresh_playlists(self, result.value()['name'])
            self.combo_pl_names.setCurrentIndex(self.combo_pl_names.findText(thislist))
    elif result.value()["type"] == 7:
        # print("    Playlist Update " + str(result.value()))
        pass


def collection_changed(self, result):
    # print("Collection Changed")
    if result.value()['namespace'] == "Playlists":
        if result.value()['type'] == 0:
            # print("    Added " + str(result.value()))
            add_new_play_list_to_playlists(self, result.value()['name'])
            this_pl = self.combo_pl_names.currentText()
            refresh_playlist_combo(self)
            self.combo_pl_names.setCurrentIndex(self.combo_pl_names.findText(this_pl))
        elif result.value()['type'] == 1:
            # print("    Collection Update " + str(result.value()))
            pass
        elif result.value()['type'] == 2:
            # print("    ReNamed " + str(result.value()))
            rename_playlist(self, result.value()['name'], result.value()['newname'])
            refresh_playlist_combo(self)
        elif result.value()['type'] == 3:
            # print("    Removed " + str(result.value()))
            self.Play_Lists[:] = [d for d in self.Play_Lists if d.get("Name") != result.value()['name']]
            refresh_playlist_combo(self)
        else:
            print("Collection changed but result is out of bounds")


def set_playstatus(self):
    status = xmmsfun.xmms_get_play_status()
    if status is not False:
        play_status_control(self, status)
    pass


def play_status_control(self, status):
    if status.value() == 0:
        self.toolStop.setDisabled(True)
        self.toolPause.hide()
        self.toolPlay.show()
        self.setWindowTitle("Dai's Xmms2 Skin")
        try:
            set_pb(self, 0)
        except AttributeError:
            pass
    elif status.value() == 1:
        self.toolStop.setDisabled(False)
        self.toolPause.show()
        self.toolPlay.hide()
    elif status.value() == 2:
        self.toolStop.setDisabled(False)
        self.toolPause.hide()
        self.toolPlay.show()
    else:
        print("    Play Status Out Of Range")


def first_set_now_stuff(self):
    ml_id = xmmsfun.xmms_get_now_playing_ml_id()
    if ml_id is None or ml_id == 0 or ml_id is False:
        return
    else:
        track = get_info_by_ml_id(self, ml_id)
        if track is not False:
            self.Now_Playing = track
            self.setWindowTitle(self.Now_Playing['title'] + "  By :  " + self.Now_Playing['artist'] +
                                "  From the Album :  " + self.Now_Playing['album'])


def set_now_stuff_from_broadcast(self, data):
    track = get_info_by_ml_id(self, data.value())
    if track is None or track is False:
        return
    self.Now_Playing = track
    self.setWindowTitle(self.Now_Playing['title'] + "  By :  " + self.Now_Playing['artist'] +
                        "  From the Album :  " + self.Now_Playing['album'])


def set_pb(self, ms):
    # noinspection PyUnresolvedReferences
    if isinstance(ms, xmmsvalue.XmmsValue):
        millisecs = ms.value()
    else:
        millisecs = ms
    if self.Now_Playing == "":
        return
    tot_time = ms_int_to_time(self.Now_Playing["duration"])
    self.progressBar.setFormat(str("%02d:%02d" % (millisecs/60000, (millisecs/1000) % 60)) + " / " + str(tot_time))
    try:
        pc = self.Now_Playing["duration"]/100
        this_pc = millisecs / float(pc)
        self.progressBar.setValue(this_pc)
    except ZeroDivisionError:
        return 0


# Playlist methods


def remove_position_from_playlists(self, pos, play_list):
    if is_in_playlists(self, play_list):
        plist = next((item for item in self.Play_Lists if item['Name'] == play_list), None)
        del plist['Ids'][pos]
        return True
    else:
        return False


def add_ml_id_to_playlists(self, ml_id, play_list):
    if is_in_playlists(self, play_list):
        plist = next((item for item in self.Play_Lists if item['Name'] == play_list), None)
        if ml_id not in plist['Ids']:
            plist['Ids'].append(ml_id)
            return True
        else:
            return False


def is_in_playlists(self, pl_name):
    for track in self.Play_Lists:
        if track['Name'] == pl_name:
            return True
    return False


def move_position_in_playlists(self, play_list, old, new):
    if is_in_playlists(self, play_list):
        plist = next((item for item in self.Play_Lists if item['Name'] == play_list), None)
        plist['Ids'].insert(new, plist['Ids'].pop(old))
        return True
    else:
        return False


def add_new_play_list_to_playlists(self, pl_name):
    self.Play_Lists.append({"Name": pl_name, "Ids": []})


def refresh_playlists(self, play_list):
    self.Play_Lists[:] = [d for d in self.Play_Lists if d.get("Name") != play_list]
    pl_ids = xmmsfun.xmms_get_playlist_entries(play_list)
    if pl_ids is not False:
        self.Play_Lists.append({"Name": play_list, "Ids": pl_ids.value()})
        # print("playlist refreshed")
        index = self.combo_pl_names.findText(play_list)
        self.combo_pl_names.setCurrentIndex(index)


def clear_playlist(self, play_list):
    self.Play_Lists[:] = [d for d in self.Play_Lists if d.get("Name") != play_list]
    self.Play_Lists.append({"Name": play_list, "Ids": []})


def refresh_playlist_combo(self):
    all_pls = []
    self.combo_pl_names.clear()
    for pl in self.Play_Lists:
        if pl['Name'].startswith("_") or pl['Name'] == "Default":
            pass
        else:
            all_pls.append(pl['Name'])
    for item in sorted(all_pls, key=lambda s: s.lower()):
        self.combo_pl_names.addItem(item)


def rename_playlist(self, oldname, newname):
    for plist in self.Play_Lists:
        if plist['Name'] == oldname:
            plist['Name'] = newname


def play_list_now(self):
    xmmsfun.xmms_clear_playlist_tracks("Default")
    this_pl = self.combo_pl_names.currentText()
    load_this_playlist(self, this_pl)
    self.tableNowPlaying.resizeColumnsToContents()
    xmmsfun.xmms_play()


def add_play_list_to_now(self):
    this_pl = self.combo_pl_names.currentText()
    load_this_playlist(self, this_pl)
    self.tableNowPlaying.resizeColumnsToContents()


def load_this_playlist(self, plist):
    thislist = get_playlist_entries_from_mem(self, plist)
    for track in thislist:
        xmmsfun.xmms_add_ml_id_to_playlist(track, 'Default')


def add_id_list_to_nowplaying(selection):
    if selection:
        for mlid in selection:
            xmmsfun.xmms_add_ml_id_to_playlist(mlid, "Default")


# Media Library methods


def set_table_with_new_values(row, table, track):
    table.item(row, 0).setText(str(track['id']))
    table.item(row, 1).setText(str(track['tracknr']))
    table.item(row, 2).setText(str(track['album']))
    table.item(row, 3).setText(str(track['partofset']))
    table.item(row, 4).setText(str(track['title']))
    table.item(row, 5).setText(str(track['artist']))
    table.item(row, 6).setText(str(track['genre']))
    table.item(row, 7).setText(str(track['performer']))
    table.item(row, 8).setText(str(ms_int_to_time(track['duration'])))
    table.item(row, 9).setText(str(track['timesplayed']))
    table.item(row, 10).setText(str(track['bitrate']))
    table.item(row, 11).setText(str(convert_to_size(track['filesize'])))


def update_ml_id_with_track(self, track):
    self.My_Library[:] = [d for d in self.My_Library if d.get('id') != track['id']]
    self.My_Library.append(track)

    np_rows = find_rows_in_table(self.tableNowPlaying, track['id'])
    if len(np_rows) > 0:
        for thisrow in np_rows:
            set_table_with_new_values(thisrow, self.tableNowPlaying, track)

    pl_rows = find_rows_in_table(self.table_pl_entries, track['id'])
    if len(pl_rows) > 0:
        for thisrow in pl_rows:
            set_table_with_new_values(thisrow, self.table_pl_entries, track)

    ml_row = find_row_in_table(self.tableMediaLibrary, track['id'])
    if ml_row is not False:
        set_table_with_new_values(ml_row, self.tableMediaLibrary, track)


def update_ml_id(self, ml_id):
    cleantrack = clean_track_result(xmmsfun.xmms_get_medialib_info_by_ml_id(ml_id))
    if cleantrack is not None:
        self.tableMediaLibrary.setSortingEnabled(False)
        update_ml_id_with_track(self, cleantrack)
        self.tableMediaLibrary.setSortingEnabled(True)
        return True
    return False


def find_rows_in_table(table, ml_id):
    lives_at = []
    for row in xrange(table.rowCount()):
        for column in xrange(1):
            item = table.item(row, column)
            if item and item.text() == str(ml_id):
                lives_at.append(table.indexFromItem(item).row())
    if not lives_at:
        return lives_at
    else:
        return lives_at


def find_row_in_table(table, ml_id):
    lives_at = False
    for row in xrange(table.rowCount()):
        for column in xrange(1):
            item = table.item(row, column)
            if item and item.text() == str(ml_id):
                lives_at = table.indexFromItem(item)
    if lives_at is False:
        return lives_at
    else:
        return lives_at.row()


def is_in_library(self, ml_id):
    for track in self.My_Library:
        if track['id'] == ml_id:
            return True
    return False


def replace_in_library(self, data):
    self.My_Library[:] = [d for d in self.My_Library if d.get('id') != data['id']]
    self.My_Library.append(data)


def remove_ml_id_from_library(self, ml_id):
    self.My_Library[:] = [d for d in self.My_Library if d.get('id') != ml_id]


def get_ml_selection(self):
    indexes = []
    ml_ids = []
    for selectionRange in self.tableMediaLibrary.selectedRanges():
        indexes.extend(range(selectionRange.topRow(), selectionRange.bottomRow() + 1))
    for i in indexes:
        mlid = self.tableMediaLibrary.item(i, 0).text()
        ml_ids.append(int(mlid))
    return ml_ids


def ml_selection_to_nowplaying(self):
    idlist = get_ml_selection(self)
    add_id_list_to_nowplaying(idlist)


def ml_selection_replace_nowplaying(self):
    idlist = get_ml_selection(self)
    xmmsfun.xmms_clear_playlist_tracks("Default")
    add_id_list_to_nowplaying(idlist)


def showdialog(self, title, question):
    # noinspection PyArgumentList
    text, ok = QInputDialog.getText(self, title, question)
    if ok:
        return text


def add_new_playlist(self):
    pl_name = showdialog(self, 'Input Dialog', 'Name for new playlist:')
    if pl_name is None or str(pl_name) is "":
        return False
    else:
        xmmsfun.xmms_create_playlist(str(pl_name))
        return pl_name


def add_id_list_to_play_list(selection, pl_name):
    if selection:
        for mlid in selection:
            xmmsfun.xmms_add_ml_id_to_playlist(mlid, pl_name)


def ml_selection_to_play_list(self, pl_name):
    idlist = get_ml_selection(self)
    add_id_list_to_play_list(idlist, pl_name)


def update_the_library(self):
    self.My_Library = []
    self.tableMediaLibrary.setRowCount(0)
    load_media_to_library(self)
    self.added_ml_ids = []


def make_playlists_from_albums(self):
    for track in self.My_Library:
        thislist = get_list_of_playlists(self)
        if track['album'] not in thislist:
            xmmsfun.xmms_create_playlist(str(track['album']))
        plist = get_playlist_entries_from_mem(self, track['album'])
        if track['id'] in plist:
            pass
        else:
            xmmsfun.xmms_add_ml_id_to_playlist(track['id'], track['album'])


def get_list_of_playlists(self):
    thislist = []
    for mylist in self.Play_Lists:
        if mylist['Name'].startswith("_") or mylist['Name'] == "Default":
            pass
        else:
            thislist.append(mylist['Name'])
    sorted_list = sorted(thislist)
    return sorted_list


def import_files(self):
    for file_with_path in QFileDialog.getOpenFileNames(self, "Import files to Xmms", os.path.expanduser("~"), ""):
        for filename in file_with_path:
            if os.path.isfile(filename):
                xmmsfun.xmms_import_file(filename)


def import_directory(self):
    dir_with_path = str(QFileDialog.getExistingDirectory(self, "Select Directory", os.path.expanduser("~")))
    if dir_with_path != "":
        if os.path.isdir(dir_with_path):
            xmmsfun.xmms_import_path(dir_with_path)


# Misc methods


def remove_entry_from_playlist(self):
    if self.table_pl_entries.currentRow() is not -1:
        plist = self.combo_pl_names.currentText()
        pl_item = self.table_pl_entries.currentRow()
        xmmsfun.xmms_remove_entry_from_playlist(int(pl_item), str(plist))


def remove_entry_from_now_playing(self):
    pl_item = self.tableNowPlaying.currentRow()
    current = xmmsfun.xmms_get_now_playing_pl_id()
    if pl_item != -1:
        if current is not False and current.value() != "no current entry":
            if pl_item == current.value()['position']:
                if not xmmsfun.xmms_next():
                    xmmsfun.xmms_stop()
                xmmsfun.xmms_remove_entry_from_now_playing_playlist(pl_item)
                return True
            else:
                xmmsfun.xmms_remove_entry_from_now_playing_playlist(pl_item)
                return True
        else:
            xmmsfun.xmms_remove_entry_from_now_playing_playlist(pl_item)
            return True


def remove_ml_id_list_from_library(self, id_list):
    for ml_id in id_list:
        if xmmsfun.xmms_medialib_remove_entry(ml_id):
            self.tableMediaLibrary.removeRow(find_row_in_table(self.tableMediaLibrary, ml_id))
            remove_ml_id_from_library(self, ml_id)


def update_new_changed_ml_id_list(self, ml_id_list):
    self.tableMediaLibrary.setSortingEnabled(False)
    for ml_id in ml_id_list:
        result = xmmsfun.xmms_get_medialib_info_by_ml_id(ml_id)
        result.wait()
        if result.is_error():
            print("Failed to add " + str(ml_id))
            continue
        track = clean_track_result(result)
        if is_in_library(self, track['id']):
            update_ml_id_with_track(self, track)
        else:
            self.My_Library.append(track)
            add_row_to_table(self.tableMediaLibrary, track)
        # print(str(ml_id) + " Added to My Library")
        self.added_ml_ids.remove(ml_id)
        self.changed_ml_ids.remove(ml_id)
    self.tableMediaLibrary.setSortingEnabled(True)


def check_now_playing_contains(ml_id_list):
    np_id_list = xmmsfun.xmms_get_now_playing_entries()
    for ml_id in ml_id_list:
        if ml_id in np_id_list.value():
            return True
    return False


def toggle_column(table, column, thebool):
    table.setColumnHidden(column, thebool)


def load_col_sizes(self):
    specs = ['table_ml_columns_size', 'table_pl_columns_size', 'table_np_columns_size']
    the_rows = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    config = SafeConfigParser()
    config.read(conffile)
    for spec in specs:
        if spec == 'table_ml_columns_size':
            for row in the_rows:
                self.tableMediaLibrary.setColumnWidth(row, int(config.get(spec, str(row))))
        elif spec == 'table_pl_columns_size':
            for row in the_rows:
                self.table_pl_entries.setColumnWidth(row, int(config.get(spec, str(row))))
        elif spec == 'table_np_columns_size':
            for row in the_rows:
                self.tableNowPlaying.setColumnWidth(row, int(config.get(spec, str(row))))


def load_config_data(self):
    load_col_sizes(self)
    specs = ['table_ml_columns_show', 'table_pl_columns_show', 'table_np_columns_show']
    ml_rbs = [self.rb_ml_0, self.rb_ml_1, self.rb_ml_2, self.rb_ml_3, self.rb_ml_4, self.rb_ml_5, self.rb_ml_6,
              self.rb_ml_7, self.rb_ml_8, self.rb_ml_9, self.rb_ml_10, self.rb_ml_11]
    pl_rbs = [self.rb_pl_0, self.rb_pl_1, self.rb_pl_2, self.rb_pl_3, self.rb_pl_4, self.rb_pl_5, self.rb_pl_6,
              self.rb_pl_7, self.rb_pl_8, self.rb_pl_9, self.rb_pl_10, self.rb_pl_11]
    np_rbs = [self.rb_np_0, self.rb_np_1, self.rb_np_2, self.rb_np_3, self.rb_np_4, self.rb_np_5, self.rb_np_6,
              self.rb_np_7, self.rb_np_8, self.rb_np_9, self.rb_np_10, self.rb_np_11]
    the_rows = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    config = SafeConfigParser()
    config.read(conffile)
    for spec in specs:
        if spec == 'table_ml_columns_show':
            for row in the_rows:
                toggle_column(self.tableMediaLibrary, row, config.get(spec, str(row)) == 'False')
                ml_rbs[row].setChecked(config.get(spec, str(row)) == 'True')
                pass
        elif spec == 'table_pl_columns_show':
            for row in the_rows:
                toggle_column(self.table_pl_entries, row, config.get(spec, str(row)) == 'False')
                pl_rbs[row].setChecked(config.get(spec, str(row)) == 'True')
                pass
        elif spec == 'table_np_columns_show':
            for row in the_rows:
                toggle_column(self.tableNowPlaying, row, config.get(spec, str(row)) == 'False')
                np_rbs[row].setChecked(config.get(spec, str(row)) == 'True')
                pass

    self.tableMediaLibrary.verticalHeader().setVisible(config.get('table_ml_columns_show', 'rows') == 'True')
    self.rb_ml_rows.setChecked(config.get('table_ml_columns_show', 'rows') == 'True')
    self.table_pl_entries.verticalHeader().setVisible(config.get('table_pl_columns_show', 'rows') == 'True')
    self.rb_pl_rows.setChecked(config.get('table_pl_columns_show', 'rows') == 'True')
    self.tableNowPlaying.verticalHeader().setVisible(config.get('table_np_columns_show', 'rows') == 'True')
    self.rb_np_rows.setChecked(config.get('table_np_columns_show', 'rows') == 'True')


def save_col_sizes(self):
    specs = ['table_ml_columns_size', 'table_pl_columns_size', 'table_np_columns_size']
    the_rows = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    config = SafeConfigParser()
    config.read(conffile)
    for spec in specs:
        if spec is 'table_ml_columns_size':
            for row in the_rows:
                if self.tableMediaLibrary.columnWidth(row) != 0:
                    config.set(spec, str(row), (str(self.tableMediaLibrary.columnWidth(row))))
        elif spec is 'table_pl_columns_size':
            for row in the_rows:
                if self.table_pl_entries.columnWidth(row) != 0:
                    config.set(spec, str(row), (str(self.table_pl_entries.columnWidth(row))))
        elif spec is 'table_np_columns_size':
            for row in the_rows:
                if self.tableNowPlaying.columnWidth(row) != 0:
                    config.set(spec, str(row), (str(self.tableNowPlaying.columnWidth(row))))

    with open(conffile, 'w') as f:
        config.write(f)


def save_config_data(self):
    specs = ['table_ml_columns_show', 'table_pl_columns_show', 'table_np_columns_show']
    ml_rbs = [self.rb_ml_0, self.rb_ml_1, self.rb_ml_2, self.rb_ml_3, self.rb_ml_4, self.rb_ml_5, self.rb_ml_6,
              self.rb_ml_7, self.rb_ml_8, self.rb_ml_9, self.rb_ml_10, self.rb_ml_11]
    pl_rbs = [self.rb_pl_0, self.rb_pl_1, self.rb_pl_2, self.rb_pl_3, self.rb_pl_4, self.rb_pl_5, self.rb_pl_6,
              self.rb_pl_7, self.rb_pl_8, self.rb_pl_9, self.rb_pl_10, self.rb_pl_11]
    np_rbs = [self.rb_np_0, self.rb_np_1, self.rb_np_2, self.rb_np_3, self.rb_np_4, self.rb_np_5, self.rb_np_6,
              self.rb_np_7, self.rb_np_8, self.rb_np_9, self.rb_np_10, self.rb_np_11]
    the_rows = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

    config = SafeConfigParser()
    config.read(conffile)

    for spec in specs:
        if spec == 'table_ml_columns_show':
            for row in the_rows:
                config.set(spec, str(row), str(ml_rbs[row].isChecked()))
        elif spec == 'table_pl_columns_show':
            for row in the_rows:
                config.set(spec, str(row), str(pl_rbs[row].isChecked()))
        elif spec == 'table_np_columns_show':
            for row in the_rows:
                config.set(spec, str(row), str(np_rbs[row].isChecked()))
    config.set('table_ml_columns_show', 'rows', str(self.rb_ml_rows.isChecked()))
    config.set('table_pl_columns_show', 'rows', str(self.rb_pl_rows.isChecked()))
    config.set('table_np_columns_show', 'rows', str(self.rb_np_rows.isChecked()))

    with open(conffile, 'w') as f:
        config.write(f)

    load_config_data(self)
    save_col_sizes(self)