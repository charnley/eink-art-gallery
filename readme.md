
# Building Your Own AI & E-Ink Powered Art Gallery

![https://charnley.github.io/blog/assets/images/eink_art/photos/front_double_landscapes.jpg](https://charnley.github.io/blog/assets/images/eink_art/photos/front_double_landscapes.jpg)


The write-up can be found at [https://charnley.github.io/blog/2025/04/02/e-ink-ai-esp32-local-art-gallery.html](https://charnley.github.io/blog/2025/04/02/e-ink-ai-esp32-local-art-gallery.html)

The different services can be found `/services/*`.

```mermaid
graph TD

    subgraph Desktop [Desktop Computer]
      direction RL
      gpucron@{ shape: rounded, label: "Cron job" }
      GPU@{ shape: rounded, label: "GPU" }
      gpucron --> GPU
    end

    subgraph HA [Home Assistant]
      database@{ shape: db, label: ".sqlite" }
      canvasserver@{ shape: rounded, label: "Picture\nServer" }
      canvasserver --> database
    end

    subgraph pictures [Picture Frames]

        subgraph esp32 [ESP32]
            esp32eink@{ shape: rounded, label: "E-Ink\nDisplay" }
        end
        subgraph rpi [Raspberry Pi Zero]
            rpieink@{ shape: rounded, label: "E-Ink\nDisplay" }
        end

        canvasserver -- "POST image" --> rpi
        esp32 -- GET image --> canvasserver

    end

    gpucron -- "GET status" --> canvasserver
    gpucron -- POST image(s) --> canvasserver
   
    classDef default stroke-width:2px;
    classDef default fill: transparent;
    classDef ParentGraph fill: transparent, stroke-width:2px;
    class pictures,HA,Desktop,esp32,rpi ParentGraph
```


- The **picture server** stores a list of AI prompts, each with its associated images, in an SQLite database. For our setup, this is hosted on **Home Assistant as an Add-on**, but it could easily run on any Docker hosting service.
- Every night, the **desktop computer** checks the picture server for prompts that need images. For each prompt, the desktop computer generates new images and sends them to the server.
- The **ESP32-powered picture frame(s)** follow a sleep schedule, staying off for 24 hours and waking up at 4 am. When it wakes up, it requests a picture, displays it, and then goes back to sleep.
- The **Raspberry Pi-powered picture frame(s)** host an API for displaying images, so you can send live notifications or images directly to the frame.


