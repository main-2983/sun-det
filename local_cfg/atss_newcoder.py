_base_ = [
    '../configs/_base_/default_runtime.py',
    '../configs/_base_/schedules/schedule_1x.py'
]

# dataset settings
dataset_type = 'CocoDataset'
classes = [
    "Beetroot", "Avocado", "Kiwi", "Peach", "Mandarine", "Orange", "Ginger",
    "Banana", "Kumquats", "Onion", "Cactus", "Plum", "Kaki", "Tomato", "Pineapple",
    "Cauliflower", "Pepper", "Melon", "Nectarine", "Papaya", "Pear", "Redcurrant",
    "Redcurrant", "Apple", "Huckleberry", "Guava", "Limes", "Granadilla", "Lemon",
    "Mango", "Strawberry", "Physalis", "Quince", "Kohlrabi", "Pepino", "Rambutan",
    "Salak", "Eggplant", "Maracuja", "Nut", "Walnut", "Grapefruit", "Mangostan",
    "Pomegranate", "Hazelnut", "Mulberry", "Tamarillo", "Tangelo", "Cantaloupe",
    "Potato", "Chestnut", "Cherry", "Clementine", "Lychee", "Apricot", "Dates",
    "Cocos", "Pomelo", "Grape", "Passion", "Carambula", "Blueberry", "Pitahaya", "Raspberry"
]
data_root = '../Dataset/FruitCOCO/'
img_norm_cfg = dict(
    mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True)
train_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(type='LoadAnnotations', with_bbox=True),
    dict(type='Resize', img_scale=(640, 640), keep_ratio=True),
    dict(type='RandomFlip', flip_ratio=0.5),
    dict(type='Normalize', **img_norm_cfg),
    dict(type='Pad', pad_to_square=True),
    dict(type='DefaultFormatBundle'),
    dict(type='Collect', keys=['img', 'gt_bboxes', 'gt_labels']),
]
test_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(
        type='MultiScaleFlipAug',
        img_scale=(640, 640),
        flip=False,
        transforms=[
            dict(type='Resize', keep_ratio=True),
            dict(type='RandomFlip'),
            dict(type='Normalize', **img_norm_cfg),
            dict(type='Pad', size_divisor=32),
            dict(type='ImageToTensor', keys=['img']),
            dict(type='Collect', keys=['img']),
        ])
]
data = dict(
    samples_per_gpu=2,
    workers_per_gpu=0,
    train=dict(
        type=dataset_type,
        ann_file=data_root + 'train/_annotations.coco.json',
        img_prefix=data_root + 'train/',
        pipeline=train_pipeline,
        classes=classes),
    val=dict(
        type=dataset_type,
        ann_file=data_root + 'valid/_annotations.coco.json',
        img_prefix=data_root + 'valid/',
        pipeline=test_pipeline,
        classes=classes),
    test=dict(
        pipeline=test_pipeline
    )
)
evaluation = dict(interval=1, metric='bbox')

model = dict(
    type='ATSS',
    backbone=dict(
        type='ResNet',
        depth=50,
        num_stages=4,
        out_indices=(0, 1, 2, 3),
        frozen_stages=1,
        norm_cfg=dict(type='BN', requires_grad=True),
        norm_eval=True,
        style='pytorch',
        init_cfg=dict(type='Pretrained', checkpoint='torchvision://resnet50')),
    neck=dict(
        type='FPN',
        in_channels=[256, 512, 1024, 2048],
        out_channels=256,
        start_level=1,
        add_extra_convs='on_output',
        num_outs=5),
    bbox_head=dict(
        type='DecoupledHead',
        num_classes=64,
        in_channels=256,
        stacked_convs=4,
        feat_channels=256,
        anchor_generator=dict(
            type='AnchorGenerator',
            ratios=[1.0],
            octave_base_scale=8,
            scales_per_octave=1,
            strides=[8, 16, 32, 64, 128]),
        bbox_coder=dict(
            type='DeltaXYWHBBoxCoder',
            target_means=[.0, .0, .0, .0],
            target_stds=[0.1, 0.1, 0.2, 0.2]),
        loss_cls=dict(
            type='FocalLoss',
            use_sigmoid=True,
            gamma=2.0,
            alpha=0.25,
            loss_weight=1.0),
        loss_bbox=dict(type='GIoULoss', loss_weight=2.0),
        loss_centerness=dict(
            type='CrossEntropyLoss', use_sigmoid=True, loss_weight=1.0)),
    # training and testing settings
    train_cfg=dict(
        assigner=dict(type='ATSSAssigner', topk=9),
        allowed_border=-1,
        pos_weight=-1,
        debug=False),
    test_cfg=dict(
        nms_pre=1000,
        min_bbox_size=0,
        score_thr=0.05,
        nms=dict(type='nms', iou_threshold=0.6),
        max_per_img=100))
# optimizer
optimizer = dict(type='SGD', lr=0.01, momentum=0.9, weight_decay=0.0001)

log_config = dict(
    interval=1,
    hooks=[
        dict(type='TextLoggerHook'),
        # dict(type='TensorboardLoggerHook')
    ])