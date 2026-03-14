import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Scanner;

public class AudioCutter {

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.println("=== Audio Cutter Java ===");
        System.out.print("Chemin du fichier audio : ");
        String inputFile = scanner.nextLine().trim();

        System.out.print("Durée des morceaux en secondes (10, 15, 30 ou autre) : ");
        int segmentSeconds = Integer.parseInt(scanner.nextLine().trim());

        if (segmentSeconds <= 0) {
            System.out.println("Erreur : la durée doit être supérieure à 0.");
            return;
        }

        File input = new File(inputFile);

        if (!input.exists()) {
            System.out.println("Erreur : fichier introuvable.");
            return;
        }

        String fileName = input.getName();
        int dotIndex = fileName.lastIndexOf('.');

        if (dotIndex == -1) {
            System.out.println("Erreur : le fichier doit avoir une extension audio.");
            return;
        }

        String baseName = fileName.substring(0, dotIndex);
        String extension = fileName.substring(dotIndex + 1);

        try {
            Path outputDir = Paths.get("output_segments");
            if (!Files.exists(outputDir)) {
                Files.createDirectories(outputDir);
            }

            String outputPattern = outputDir.resolve(baseName + "_%03d." + extension).toString();

            ProcessBuilder processBuilder = new ProcessBuilder(
                "ffmpeg",
                "-i", inputFile,
                "-f", "segment",
                "-segment_time", String.valueOf(segmentSeconds),
                "-c", "copy",
                outputPattern
            );

            processBuilder.inheritIO();
            Process process = processBuilder.start();
            int exitCode = process.waitFor();

            if (exitCode == 0) {
                System.out.println("Découpe terminée.");
                System.out.println("Les morceaux sont dans le dossier : output_segments");
            } else {
                System.out.println("Erreur pendant la découpe.");
            }

        } catch (IOException | InterruptedException e) {
            System.out.println("Erreur : " + e.getMessage());
        }
    }
}
