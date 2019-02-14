from __future__ import division
import os
import time
from glob import glob
import tensorflow as tf
import numpy as np
from collections import namedtuple
import random

from module import *
from utils import *

class cyclegan(object):
    def __init__(self, sess, args):
        self.sess = sess
        self.batch_size = args.batch_size
        self.image_size = args.fine_size
        self.input_c_dim = args.input_nc
        self.output_c_dim = args.output_nc
        self.L1_lambda = args.L1_lambda
        self.which_expression = args.which_expression
        self.new_file = args.new_file
        self.new_file_name = args.new_file_name
        self.checkpoint_dir = args.checkpoint_dir
        self.more_button = args.more_button

        self.discriminator = discriminator
        if args.use_resnet:
            self.generator = generator_resnet
        else:
            self.generator = generator_unet
        if args.use_lsgan:
            self.criterionGAN = mae_criterion
        else:
            self.criterionGAN = sce_criterion

    def _build_model(self):
        self.real_data = tf.placeholder(tf.float32,
                                        [None, self.image_size, self.image_size,
                                         self.input_c_dim + self.output_c_dim],
                                        name='real_A_and_B_images')

        self.real_A = self.real_data[:, :, :, :self.input_c_dim]
        self.real_B = self.real_data[:, :, :, self.input_c_dim:self.input_c_dim + self.output_c_dim]

        self.fake_B = self.generator(self.real_A, self.options, False, name="generatorA2B")
        self.fake_A_ = self.generator(self.fake_B, self.options, False, name="generatorB2A")
        self.fake_A = self.generator(self.real_B, self.options, True, name="generatorB2A")
        self.fake_B_ = self.generator(self.fake_A, self.options, True, name="generatorA2B")

        self.DB_fake = self.discriminator(self.fake_B, self.options, reuse=False, name="discriminatorB")
        self.DA_fake = self.discriminator(self.fake_A, self.options, reuse=False, name="discriminatorA")
        self.g_loss_a2b = self.criterionGAN(self.DB_fake, tf.ones_like(self.DB_fake)) \
                          + self.L1_lambda * abs_criterion(self.real_A, self.fake_A_) \
                          + self.L1_lambda * abs_criterion(self.real_B, self.fake_B_)
        self.g_loss_b2a = self.criterionGAN(self.DA_fake, tf.ones_like(self.DA_fake)) \
                          + self.L1_lambda * abs_criterion(self.real_A, self.fake_A_) \
                          + self.L1_lambda * abs_criterion(self.real_B, self.fake_B_)
        self.g_loss = self.criterionGAN(self.DA_fake, tf.ones_like(self.DA_fake)) \
                      + self.criterionGAN(self.DB_fake, tf.ones_like(self.DB_fake)) \
                      + self.L1_lambda * abs_criterion(self.real_A, self.fake_A_) \
                      + self.L1_lambda * abs_criterion(self.real_B, self.fake_B_)

        self.fake_A_sample = tf.placeholder(tf.float32,
                                            [None, self.image_size, self.image_size,
                                             self.input_c_dim], name='fake_A_sample')
        self.fake_B_sample = tf.placeholder(tf.float32,
                                            [None, self.image_size, self.image_size,
                                             self.output_c_dim], name='fake_B_sample')
        self.DB_real = self.discriminator(self.real_B, self.options, reuse=True, name="discriminatorB")
        self.DA_real = self.discriminator(self.real_A, self.options, reuse=True, name="discriminatorA")
        self.DB_fake_sample = self.discriminator(self.fake_B_sample, self.options, reuse=True, name="discriminatorB")
        self.DA_fake_sample = self.discriminator(self.fake_A_sample, self.options, reuse=True, name="discriminatorA")

        self.db_loss_real = self.criterionGAN(self.DB_real, tf.ones_like(self.DB_real))
        self.db_loss_fake = self.criterionGAN(self.DB_fake_sample, tf.zeros_like(self.DB_fake_sample))
        self.db_loss = (self.db_loss_real + self.db_loss_fake) / 2
        self.da_loss_real = self.criterionGAN(self.DA_real, tf.ones_like(self.DA_real))
        self.da_loss_fake = self.criterionGAN(self.DA_fake_sample, tf.zeros_like(self.DA_fake_sample))
        self.da_loss = (self.da_loss_real + self.da_loss_fake) / 2
        self.d_loss = self.da_loss + self.db_loss

        self.g_loss_a2b_sum = tf.summary.scalar("g_loss_a2b", self.g_loss_a2b)
        self.g_loss_b2a_sum = tf.summary.scalar("g_loss_b2a", self.g_loss_b2a)
        self.g_loss_sum = tf.summary.scalar("g_loss", self.g_loss)
        self.g_sum = tf.summary.merge([self.g_loss_a2b_sum, self.g_loss_b2a_sum, self.g_loss_sum])
        self.db_loss_sum = tf.summary.scalar("db_loss", self.db_loss)
        self.da_loss_sum = tf.summary.scalar("da_loss", self.da_loss)
        self.d_loss_sum = tf.summary.scalar("d_loss", self.d_loss)
        self.db_loss_real_sum = tf.summary.scalar("db_loss_real", self.db_loss_real)
        self.db_loss_fake_sum = tf.summary.scalar("db_loss_fake", self.db_loss_fake)
        self.da_loss_real_sum = tf.summary.scalar("da_loss_real", self.da_loss_real)
        self.da_loss_fake_sum = tf.summary.scalar("da_loss_fake", self.da_loss_fake)
        self.d_sum = tf.summary.merge(
            [self.da_loss_sum, self.da_loss_real_sum, self.da_loss_fake_sum,
             self.db_loss_sum, self.db_loss_real_sum, self.db_loss_fake_sum,
             self.d_loss_sum]
        )

        self.test_A = tf.placeholder(tf.float32,
                                     [None, self.image_size, self.image_size,
                                      self.input_c_dim], name='test_A')
        self.test_B = tf.placeholder(tf.float32,
                                     [None, self.image_size, self.image_size,
                                      self.output_c_dim], name='test_B')
        self.testB = self.generator(self.test_A, self.options, True, name="generatorA2B")
        self.testA = self.generator(self.test_B, self.options, True, name="generatorB2A")

        t_vars = tf.trainable_variables()
        self.d_vars = [var for var in t_vars if 'discriminator' in var.name]
        self.g_vars = [var for var in t_vars if 'generator' in var.name]
        for var in t_vars: print(var.name)

    #checkpoint 불러옴 (model 불러옴)
    def load(self):
        print(" [*] Reading checkpoint...")

        background_flag = random.randrange(1, 3)

        if self.which_expression == 'happy' and self.more_button == False:
            model_dir = "%s_%s" % ('summer2winter_yosemite', self.image_size)
        elif self.which_expression == 'angry' and self.more_button == False:
            model_dir = "%s_%s" % ('summer2autumn_yosemite', self.image_size)
        elif self.which_expression == 'blue' and self.more_button == False:
            model_dir = "%s_%s" % ('summer2winter_yosemite', self.image_size)
        else:
            if background_flag == 1:
                model_dir = "%s_%s" % ('summer2winter_yosemite', self.image_size)
            else:
                model_dir = "%s_%s" % ('summer2autumn_yosemite', self.image_size)
        checkpoint_dir = os.path.join(self.checkpoint_dir, model_dir)

        ckpt = tf.train.get_checkpoint_state(checkpoint_dir)

        if ckpt and ckpt.model_checkpoint_path:
            ckpt_name = os.path.basename(ckpt.model_checkpoint_path)
            self.saver.restore(self.sess, os.path.join(checkpoint_dir, ckpt_name))
            return True
        else:
            return False


    def test(self, args):
        """Test cyclegan"""

        direction_flag = random.randrange(1, 3)

        if self.which_expression == 'happy' and self.more_button == False:
            which_direction = 'BtoA'
        elif self.which_expression == 'angry' and self.more_button == False:
            which_direction = 'AtoB'
        elif self.which_expression == 'blue' and self.more_button == False:
            which_direction = 'AtoB'
        else:
            if direction_flag == 1:
                which_direction = 'AtoB'
            else:
                which_direction = 'BtoA'

        #새로운 파일
        sample_files = ['./public/upload/'+self.new_file]
        #sample_files = ['datasets/' + self.new_file]

        print(sample_files)
        # write html for visual comparison
        index_path = os.path.join(args.test_dir, '{0}_index.html'.format(which_direction))
        index = open(index_path, "w")
        index.write("<html><body><table><tr>")
        index.write("<th>name</th><th>input</th><th>output</th></tr>")

        out_var, in_var = (self.testB, self.test_A) if which_direction == 'AtoB' else (
            self.testA, self.test_B)


        print('Processing image: ' + sample_files[0])
        sample_image = [load_test_data(sample_files[0], args.fine_size)]
        sample_image = np.array(sample_image).astype(np.float32)
        image_path = './public/upload/'+self.new_file_name

        #image_path = os.path.join(args.test_dir,
        #                          '{0}_{1}'.format(which_direction, os.path.basename(sample_files[0])))
        fake_img = self.sess.run(out_var, feed_dict={in_var: sample_image})
        save_images(fake_img, [1, 1], image_path)
        index.write("<td>%s</td>" % os.path.basename(image_path))
        index.write("<td><img src='%s'></td>" % (sample_files[0] if os.path.isabs(sample_files[0]) else (
                '..' + os.path.sep + sample_files[0])))
        index.write("<td><img src='%s'></td>" % (image_path if os.path.isabs(image_path) else (
                '..' + os.path.sep + image_path)))
        index.write("</tr>")
        if which_direction == 'AtoB':
            print("AtoB_index.html", "r")
        elif which_direction == 'BtoA':
            print("BtoA_index.html", "r")

        self.more_button = False

        index.close()
        print(1)
