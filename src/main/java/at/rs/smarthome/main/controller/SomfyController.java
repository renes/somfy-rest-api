package at.rs.smarthome.main.controller;

import at.rs.smarthome.main.dto.Blind;
import at.rs.smarthome.main.dto.Command;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

import java.io.File;
import java.io.IOException;
import java.util.concurrent.TimeUnit;

@RestController
public class SomfyController {

    private static final Logger LOGGER = LoggerFactory.getLogger(SomfyController.class);

    @GetMapping("/somfy/{blind}/{command}")
    public ResponseEntity executeCommand(@PathVariable Blind blind, @PathVariable Command command) throws IOException, InterruptedException {

        ProcessBuilder pb = new ProcessBuilder("/usr/bin/python", "somfy.py", blind.toString().toLowerCase(), command.toString().toLowerCase());

        pb.directory(new File("/home/pi/somfy/"));
        Process p = pb.start();
        p.waitFor(2, TimeUnit.SECONDS);
        LOGGER.info(String.valueOf(p.exitValue()));

        return ResponseEntity.ok().build();
    }
}