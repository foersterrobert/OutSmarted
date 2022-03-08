import 'dart:async';
import 'dart:io';

import 'package:camera/camera.dart';
import 'package:flutter/material.dart';

import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  final cameras = await availableCameras();
  final firstCamera = cameras.first;

  runApp(
    MaterialApp(
      theme: ThemeData.dark(),
      home: TakePictureScreen(
        camera: firstCamera,
      ),
    ),
  );
}

// A screen that allows users to take a picture using a given camera.
class TakePictureScreen extends StatefulWidget {
  const TakePictureScreen({
    Key? key,
    required this.camera,
  }) : super(key: key);

  final CameraDescription camera;

  @override
  TakePictureScreenState createState() => TakePictureScreenState();
}

class TakePictureScreenState extends State<TakePictureScreen> {
  late CameraController _controller;
  late Future<void> _initializeControllerFuture;

  @override
  void initState() {
    super.initState();
    _controller = CameraController(
      widget.camera,
      ResolutionPreset.high,
    );
    _initializeControllerFuture = _controller.initialize();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('OutSmarted')),
      body: Column(children: [
        Row(
          children: [
            Expanded(
              child: GestureDetector(
                onTap: () async {
                  try {
                    await _initializeControllerFuture;
                    final image = await _controller.takePicture();
                    var request = http.MultipartRequest(
                        "POST", Uri.parse("http://10.0.2.2:5000/"));
                    request.files.add(await http.MultipartFile.fromPath(
                        "image", 
                        image.path,
                        contentType: MediaType("image", "jpeg")
                    ));
                    var response = await request.send();

                  } catch (e) {
                    print(e);
                  }
                },
                child: Padding(
                  padding: EdgeInsets.all(32.0),
                  child: AspectRatio(
                    aspectRatio: 1,
                    child: ClipRect(
                      child: Transform.scale(
                        scale: _controller.value.aspectRatio,
                        child: FutureBuilder<void>(
                          future: _initializeControllerFuture,
                          builder: (context, snapshot) {
                            if (snapshot.connectionState == ConnectionState.done) {
                              // If the Future is complete, display the preview.
                              return CameraPreview(_controller);
                            } else {
                              // Otherwise, display a loading indicator.
                              return const Center(child: CircularProgressIndicator());
                            }
                          },
                        ),
                      ),
                    ),
                  )
                )
              )
            )
          ],
        ),
        Row(
          children: [
            const Expanded(
              child: Text('Scan Bord by tapping Camera', textAlign: TextAlign.center,),
            )
          ],
        )
      ],
      )
    );
  }
}

class DisplayPictureScreen extends StatelessWidget {
  final String imagePath;

  const DisplayPictureScreen({Key? key, required this.imagePath})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Display the Picture')),
      body: Image.file(File(imagePath)),
    );
  }
}
