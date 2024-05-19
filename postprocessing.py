from pydub import AudioSegment

def replace_audio_segment(original_audio, new_audio, position_start, position_end):
    new_audio = new_audio[new_audio.duration_seconds * 1000 * 0.15:new_audio.duration_seconds * 1000 * 0.8]
    before_position = original_audio[:position_start]
    after_position = original_audio[position_end:]

    average_dBFS_original = abs(original_audio.dBFS)

    average_dBFS_new = abs(new_audio.dBFS)
    print(average_dBFS_new, average_dBFS_original)
    gain_difference = average_dBFS_original - average_dBFS_new

    new_audio_adjusted = new_audio.apply_gain(gain_difference)

    faded_new_audio = new_audio_adjusted.fade_in(10).fade_out(10)

    # replaced_audio = before_position + new_audio_adjusted + after_position

    replaced_audio = before_position + faded_new_audio + after_position
    # replaced_audio = before_position + new_audio + after_position

    return replaced_audio


original_audio = AudioSegment.from_file("/home/dasha/python_diplom/wav/user_v.2.wav")
new_audio = AudioSegment.from_file("/home/dasha/python_diplom/temp_wav/круто.wav")
position_to_replace = 2200  # Пример позиции, с которой будет производиться замена

updated_audio = replace_audio_segment(original_audio, new_audio, 3004, 3466)
updated_audio.export("updated_audio.wav", format="wav")