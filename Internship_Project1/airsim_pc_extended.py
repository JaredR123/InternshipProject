#!/usr/bin/env python
import airsim
import glooey
import imgviz
import numpy as np
import cv2
import pyglet
import trimesh
import trimesh.transformations as tf
import trimesh.viewer
import pandas as pd

#import sys
#sys.path.append('/home/vishnuds/research/inpaint/octomap-python/')
import octomap


def pointcloud_from_depth(depth, fx, fy, cx, cy):
    assert depth.dtype.kind == 'f', 'depth must be float and have meter values'

    rows, cols = depth.shape
    c, r = np.meshgrid(np.arange(cols), np.arange(rows), sparse=True)
    valid = ~np.isnan(depth)
    z = np.where(valid, depth, np.nan)
    x = np.where(valid, z * (c - cx) / fx, np.nan)
    y = np.where(valid, z * (r - cy) / fy, np.nan)
    pc = np.dstack((x, y, z))

    return pc


def labeled_scene_widget(scene, label):
    vbox = glooey.VBox()
    vbox.add(glooey.Label(text=label, color=(255, 255, 255)), size=0)
    vbox.add(trimesh.viewer.SceneWidget(scene))
    return vbox


def visualize(
    occupied, empty, K, width, height, rgb, pcd, mask, resolution, aabb
):
    window = pyglet.window.Window(
        width=int(width * 0.9 * 3), height=int(height * 0.9)
    )

    @window.event
    def on_key_press(symbol, modifiers):
        if modifiers == 0:
            if symbol == pyglet.window.key.Q:
                window.on_close()

    gui = glooey.Gui(window)
    hbox = glooey.HBox()
    hbox.set_padding(5)

    camera = trimesh.scene.Camera(
        resolution=(width, height), focal=(K[0, 0], K[1, 1])
    )
    camera_marker = trimesh.creation.camera_marker(camera, marker_height=0.1)

    # initial camera pose
    camera_transform = np.array(
        [
            [0.73256052, -0.28776419, 0.6168848, 0.66972396],
            [-0.26470017, -0.95534823, -0.13131483, -0.12390466],
            [0.62712751, -0.06709345, -0.77602162, -0.28781298],
            [0.0, 0.0, 0.0, 1.0],
        ],
    )

    aabb_min, aabb_max = aabb
    bbox = trimesh.path.creation.box_outline(
        aabb_max - aabb_min,
        tf.translation_matrix((aabb_min + aabb_max) / 2),
    )

    geom = trimesh.PointCloud(vertices=pcd[mask], colors=rgb[mask])
    scene = trimesh.Scene(camera=camera, geometry=[bbox, geom, camera_marker])
    scene.camera_transform = camera_transform
    hbox.add(labeled_scene_widget(scene, label='pointcloud'))

    geom = trimesh.voxel.ops.multibox(
        occupied, pitch=resolution, colors=[1.0, 0, 0, 0.5]
    )
    scene = trimesh.Scene(camera=camera, geometry=[bbox, geom, camera_marker])
    scene.camera_transform = camera_transform
    hbox.add(labeled_scene_widget(scene, label='occupied'))

    geom = trimesh.voxel.ops.multibox(
        empty, pitch=resolution, colors=[0.5, 0.5, 0.5, 0.5]
    )
    scene = trimesh.Scene(camera=camera, geometry=[bbox, geom, camera_marker])
    scene.camera_transform = camera_transform
    hbox.add(labeled_scene_widget(scene, label='empty'))

    gui.add(hbox)
    pyglet.app.run()


def main():
    
    imageWidth = 640#256
    imageHeight = 480#144
    
    '''
    client = airsim.MultirotorClient()
    cameraFOV = client.simGetCameraInfo('0').fov
    
    f = imageWidth/(2 * np.tan(cameraFOV*np.pi / 360))
    Cu = imageWidth//2
    Cv = imageHeight//2
    K = np.array([[f, 0, Cu], [0, f, Cv], [0, 0, 1]])

    rawDepth = client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.DepthPlanner, True)])[0]#Or depth perspective?
    rawColor = client.simGetImage("0", airsim.ImageType.Scene)
    #depth_png = cv2.imdecode(np.frombuffer(rawDepth, np.float32) , cv2.IMREAD_UNCHANGED)
    rgb = cv2.imdecode(np.frombuffer(rawColor, np.uint8) , cv2.IMREAD_UNCHANGED)[:,:,:3]
    depth_png = np.array(rawDepth.image_data_float, dtype=np.float32).reshape(rgb.shape[:2])
    
    np.save('rgb_airsim.npy', rgb)
    np.save('depth_airsim.npy', depth_png)
    np.save('camera_K.npy', K)
    '''
    index_i = 1
    rgb = np.load(f'../../airsim_data/frame_{index_i:03d}_rgb.npy')
    depth_png = np.load(f'../../airsim_data/depth_{index_i:03d}.npy')
    df = pd.read_csv('../../airsim_data/postion.csv')

    K = np.load('camera_K.npy')

    pcd = pointcloud_from_depth(
            depth_png, fx=K[0, 0], fy=K[1, 1], cx=K[0, 2], cy=K[1, 2]
    )


    nonnan = ~np.isnan(pcd).any(axis=2)
    mask = np.less(pcd[:, :, 2], 400) #np.less(pcd[:, :, 2], 2)
    print(f'masked/total: {np.sum(mask)}/{imageWidth*imageHeight}')
    resolution = 1. #0.01
    octree = octomap.OcTree(resolution)
    octree.insertPointCloud(
        pointcloud=pcd[nonnan],
        origin=df.iloc[index_i-1,:3].values,
        maxrange=400,
    )
    occupied, empty = octree.extractPointCloud()
    print(f'Occupied: {occupied.shape}, Empty: {empty.shape}')

    aabb_min = octree.getMetricMin()
    aabb_max = octree.getMetricMax()

    visualize(
        occupied=occupied,
        empty=empty,
        K=K,
        width=imageWidth,#camera_info['width'],
        height=imageHeight,#camera_info['height'],
        rgb=rgb,
        pcd=pcd,
        mask=mask,
        resolution=resolution,
        aabb=(aabb_min, aabb_max),
    )


if __name__ == '__main__':
    main()
