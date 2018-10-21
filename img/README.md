Place Static Images here in .jpg, .jpeg, .gif, .png, or .bmp format

Set your bots.local.yaml file with the following settings:

```
public_url: <public facing base url to reach Flask app>
img:
  path: <local path to img folder>
  dest: <url extension to server to>
```

And you will be able to reference images via {{ public_url }}/{{ dest }}/{{ filename }}
