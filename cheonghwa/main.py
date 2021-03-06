import argparse
import os
import tensorflow as tf
tf.set_random_seed(19)
from model import cyclegan
from collections import namedtuple

parser = argparse.ArgumentParser(description='')
parser.add_argument('--which_direction', dest='which_direction', default='AtoB', help='AtoB or BtoA')
parser.add_argument('--which_expression', dest='which_expression', default='happy', help='happy, angry')
parser.add_argument('--test_dir', dest='test_dir', default='./cheonghwa/test', help='test sample are saved here')
parser.add_argument('--new_file', dest='new_file', default='1.jpg', help='test sample are saved here')
parser.add_argument('--checkpoint_dir', dest='checkpoint_dir', default='./cheonghwa/checkpoint', help='models are saved here')
parser.add_argument('--more_button', dest='more_button', default=True, help='more_button flag')
parser.add_argument('--new_file_name', dest='new_file_name', default='small_2018-08-30-11-11-55_result.jpg', help='.')

parser.add_argument('--epoch', dest='epoch', type=int, default=200, help='# of epoch')
parser.add_argument('--epoch_step', dest='epoch_step', type=int, default=100, help='# of epoch to decay lr')
parser.add_argument('--batch_size', dest='batch_size', type=int, default=1, help='# images in batch')
parser.add_argument('--load_size', dest='load_size', type=int, default=286, help='scale images to this size')
parser.add_argument('--fine_size', dest='fine_size', type=int, default=256, help='then crop to this size')
parser.add_argument('--ngf', dest='ngf', type=int, default=64, help='# of gen filters in first conv layer')
parser.add_argument('--ndf', dest='ndf', type=int, default=64, help='# of discri filters in first conv layer')
parser.add_argument('--input_nc', dest='input_nc', type=int, default=3, help='# of input image channels')
parser.add_argument('--output_nc', dest='output_nc', type=int, default=3, help='# of output image channels')
parser.add_argument('--lr', dest='lr', type=float, default=0.0002, help='initial learning rate for adam')
parser.add_argument('--beta1', dest='beta1', type=float, default=0.5, help='momentum term of adam')
parser.add_argument('--phase', dest='phase', default='test', help='test')
parser.add_argument('--save_freq', dest='save_freq', type=int, default=1000, help='save a model every save_freq iterations')
parser.add_argument('--print_freq', dest='print_freq', type=int, default=100, help='print the debug information every print_freq iterations')
parser.add_argument('--continue_train', dest='continue_train', type=bool, default=False, help='if continue training, load the latest model: 1: true, 0: false')
parser.add_argument('--L1_lambda', dest='L1_lambda', type=float, default=10.0, help='weight on L1 term in objective')
parser.add_argument('--use_resnet', dest='use_resnet', type=bool, default=True, help='generation network using reidule block')
parser.add_argument('--use_lsgan', dest='use_lsgan', type=bool, default=True, help='gan loss defined in lsgan')
parser.add_argument('--max_size', dest='max_size', type=int, default=50, help='max size of image pool, 0 means do not use image pool')

args = parser.parse_args()

def main(_):
    if not os.path.exists(args.checkpoint_dir):
        os.makedirs(args.checkpoint_dir)
    if not os.path.exists(args.test_dir):
        os.makedirs(args.test_dir)

    tfconfig = tf.ConfigProto(allow_soft_placement=True)
    tfconfig.gpu_options.allow_growth = True
    with tf.Session(config=tfconfig) as sess:
        model = cyclegan(sess, args)

        #model 불러옴
        OPTIONS = namedtuple('OPTIONS', 'batch_size image_size \
                              gf_dim df_dim output_c_dim is_training')
        model.options = OPTIONS._make((args.batch_size, args.fine_size,
                                       args.ngf, args.ndf, args.output_nc,
                                       args.phase == 'train'))
        model._build_model()
        model.saver = tf.train.Saver()

        #for 문

        while(1):
            print('py ready')

            #동호오빠가 넘겨줄 부분 (0 : 파일이름, 1:확장자, 2:표정, 3: more 버튼이 눌렸는지)
            lines = input().split(',')
            args.new_file = lines[0]+'.'+lines[1]
            args.which_expression = lines[2]
            args.more_button = lines[3]
            args.new_file_name = lines[0]+'_result.'+lines[1]
            if lines[0] == 99 :
                break

            if model.load():
                print(" [*] Load SUCCESS")
            else:
                print(" [*] Load Failed...")
            model.test(args)


if __name__ == '__main__':
    tf.app.run()

