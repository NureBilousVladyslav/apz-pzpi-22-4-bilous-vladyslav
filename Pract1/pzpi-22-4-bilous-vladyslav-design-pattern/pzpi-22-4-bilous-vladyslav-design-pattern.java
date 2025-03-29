// Об'єктний адаптер
interface MediaPlayer {
    void play(String audioType, String fileName);
}

class AdvancedMediaPlayer {
    void playMp4(String fileName) {
        System.out.println("Playing mp4 file: " + fileName);
    }
}

class MediaAdapter implements MediaPlayer {
    private AdvancedMediaPlayer advancedMediaPlayer;

    public MediaAdapter() {
        this.advancedMediaPlayer = new AdvancedMediaPlayer();
    }
    
    @Override
    public void play(String audioType, String fileName) {
        if ("mp4".equalsIgnoreCase(audioType)) {
            advancedMediaPlayer.playMp4(fileName);
        }
    }
}

// Класовий адаптер
interface MediaPlayer {
    void play(String audioType, String fileName);
}

class AdvancedMediaPlayer {
    void playMp4(String fileName) {
        System.out.println("Playing mp4 file: " + fileName);
    }
}

class MediaAdapter extends AdvancedMediaPlayer implements MediaPlayer {
    @Override
    public void play(String audioType, String fileName) {
        if ("mp4".equalsIgnoreCase(audioType)) {
            playMp4(fileName);
        }
    }
}