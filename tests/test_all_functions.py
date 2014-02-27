#!/usr/bin/env python

"""test each function in the wg-fast
code"""

import unittest
from wg_fast.util import *
import os
import tempfile
import shutil
import re

curr_dir=os.getcwd()

class Test1(unittest.TestCase):
    def test_get_seq_name_basic_function(self):
        self.assertEqual(get_seq_name("/path/to/test.fasta"), "test.fasta")
    """tests the condition where you use a tilda instead of full path"""
    def test_get_seq_name_tilda(self):
        self.assertEqual(get_seq_name("~/test.fasta"), "test.fasta")
    """tests the case where no path is passed"""
    def test_get_seq_name_empty(self):
        self.assertEqual(get_seq_name(""), "")
    """tests the case where something weird is passed"""
    def test_get_seq_name_wrong_slash(self):
        self.assertEqual(get_seq_name("\wrong\way"), "\\wrong\\way")

class Test2(unittest.TestCase):
    def test_get_readFile_components_basic_function(self):
        self.assertEqual(get_readFile_components("/path/to/file.gz"), ('/path/to', 'file', '.gz'))
    def test_get_readFile_components_tilda(self):
        self.assertEqual(get_readFile_components("~/path/to/file.gz"), ('~/path/to', 'file', '.gz'))
    def test_get_readFile_components_non_gz(self):
        self.assertEqual(get_readFile_components("~/path/to/file.fasta"), ('~/path/to', 'file', '.fasta'))
    def test_get_readFile_components_wrong_slash(self):
        self.assertEqual(get_readFile_components("~\path\to\file.fasta"), ('', '~\\path\to\x0cile', '.fasta'))
    def test_get_readFile_components_empty(self):
        self.assertEqual(get_readFile_components(""), ('', '', ''))

class Test4(unittest.TestCase):
    def test_process_vcf_reference_case(self):
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"testfile.filtered.vcf")
        fp = open(fpath, "w")
        fp.write("##fileformat=VCFv4.1\n")
        fp.write("#CHROM  POS     ID      REF     ALT     QUAL    FILTER  INFO    FORMAT  vac6wt\n")
        fp.write("ADK1    454     .       A       .       154     .       AN=1;DP=5;MQ=60.00;MQ0=0        GT:DP:MLPSAC:MLPSAF     0:5\n")
        fp.close()
        self.assertEqual(process_vcf(fpath, ["ADK1::454"], 4, 0.9, "tmp"), ["ADK1::454::A"])
        shutil.rmtree(tdir)
    def test_process_vcf_SNP_case(self):
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"testfile.filtered.vcf")
        fp = open(fpath, "w")
        fp.write("##fileformat=VCFv4.1\n")
        fp.write("#CHROM  POS     ID      REF     ALT     QUAL    FILTER  INFO    FORMAT  vac6wt\n")
        fp.write("ADK1    460     .       A       G       79      .       AC=1;AF=1.00;AN=1;DP=5;Dels=0.00;FS=0.000;HaplotypeScore=0.0000;MLEAC=1;MLEAF=1.00;MQ=60.00;MQ0=0;QD=15.80      GT:AD:DP:GQ:MLPSAC:MLPSAF:PL    1:0,5:5:99:1:1.00:109,0")
        fp.close()
        self.assertEqual(process_vcf(fpath, ["ADK1::460"],4, 0.9, "tmp"), ["ADK1::460::G"])
        shutil.rmtree(tdir)
    def test_process_vcf_other_cases(self):
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"testfile.filtered.vcf")
        fp = open(fpath, "w")
        fp.write("##fileformat=VCFv4.1\n")
        fp.write("#CHROM  POS     ID      REF     ALT     QUAL    FILTER  INFO    FORMAT  vac6wt\n")
        fp.write("ADK1    460     .       A       G       79      .       AC=1;AF=1.00;AN=1;DP=5;Dels=0.00;FS=0.000;HaplotypeScore=0.0000;MLEAC=1;MLEAF=1.00;MQ=60.00;MQ0=0;QD=15.80      GT:AD:DP:GQ:MLPSAC:MLPSAF:PL    1:0,5:5:99:1:1.00:109,0\n")
        fp.write("ADK1    454     .       A       .       154     .       AN=1;DP=5;MQ=60.00;MQ0=0        GT:DP:MLPSAC:MLPSAF     0:5\n")
        fp.close()
        self.assertEqual(process_vcf(fpath, ["ADK1::460", "ADK1::454"], 6, 0.9, "tmp"), ["ADK1::460::-", "ADK1::454::-"])
        shutil.rmtree(tdir)
    def test_process_vcf_proportion(self):
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"testfile.filtered.vcf")
        fp = open(fpath, "w")
        fp.write("##fileformat=VCFv4.1\n")
        fp.write("#CHROM  POS     ID      REF     ALT     QUAL    FILTER  INFO    FORMAT  vac6wt\n")
        fp.write("ADK1    460     .       A       G       79      .       AC=1;AF=1.00;AN=1;DP=6;Dels=0.00;FS=0.000;HaplotypeScore=0.0000;MLEAC=1;MLEAF=1.00;MQ=60.00;MQ0=0;QD=15.80      GT:AD:DP:GQ:MLPSAC:MLPSAF:PL    1:1,5:6:99:1:1.00:109,0\n")
        fp.close()
        self.assertEqual(process_vcf(fpath, ["ADK1::460"], 5, 0.9, "tmp"), ["ADK1::460::-"])
        shutil.rmtree(tdir)
        
class Test5(unittest.TestCase):
    def test_sort_information_basic_function(self):
        self.assertEqual(sort_information("ADK1::460"), 460)
    def test_sort_information_cant_parse(self):
        self.assertRaises(TypeError, sort_information, "ADK1__460")
    def test_sort_information_no_input(self):
        self.assertRaises(TypeError, sort_information, None)
        
class Test6(unittest.TestCase):
    def test_matrix_to_fasta_basic_function(self):
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"testfile.filtered.vcf")
        fp = open(fpath, "w")
        fp.write("LocusID\tReference\tgenome1\tgenome2\n")
        fp.write("ADK::1\tA\tT\tT\n")
        fp.write("ADK::2\tT\tT\tT\n")
        fp.close()
        self.assertEqual(matrix_to_fasta(fpath), [">ReferenceAT", ">genome1TT", ">genome2TT"])
        shutil.rmtree(tdir)
    def test_matrix_to_fasta_unequal_fields(self):
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"testfile.filtered.vcf")
        fp = open(fpath, "w")
        fp.write("LocusID\tReference\tgenome1\tgenome2\n")
        fp.write("ADK::1\tA\tT\tT\n")
        fp.write("ADK::2\tT\tT\n")
        fp.close()
        self.assertEqual(matrix_to_fasta(fpath), [">ReferenceAT", ">genome1TT"])
        shutil.rmtree(tdir)
    def test_matrix_to_fasta_multiple_states(self):
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"testfile.filtered.vcf")
        fp = open(fpath, "w")
        fp.write("LocusID\tReference\tgenome1\tgenome2\n")
        fp.write("ADK::1\tA\tT\tT\n")
        fp.write("ADK::2\tT\tT\tTT\n")
        fp.close()
        self.assertEqual(matrix_to_fasta(fpath), [">ReferenceAT", ">genome1TT", ">genome2TTT"])
        shutil.rmtree(tdir)
        
class Test7(unittest.TestCase):
    def test_write_reduced_matrix_basic_function(self):
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"testfile.filtered.vcf")
        fp = open(fpath, "w")
        fp.write("LocusID\tReference\tgenome1\tgenome2\t#SNPcall\n")
        fp.write("ADK::1\tA\tT\tT\n")
        fp.write("ADK::2\tT\tT\tT\n")
        fp.close()
        self.assertEqual(write_reduced_matrix(fpath), [4, 4])
        shutil.rmtree(tdir)
    def test_write_reduced_matrix_odd_field_numbers(self):
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"testfile.filtered.vcf")
        fp = open(fpath, "w")
        fp.write("LocusID\tReference\tgenome1\tgenome2\t#SNPcall\n")
        fp.write("ADK::1\tA\tT\tT\n")
        fp.write("ADK::2\tT\tT\n")
        fp.close()
        self.assertEqual(write_reduced_matrix(fpath), [4, 3])
        shutil.rmtree(tdir)
        
class Test8(unittest.TestCase):
    def test_make_temp_matrix_basic_function(self):
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"testfile.matrix")
        fp = open(fpath, "w")
        fp.write("LocusID\tReference\tgenome1\tgenome2\n")
        fp.write("ADK::1\tA\tT\tT\n")
        fp.write("ADK::2\tT\tT\tT\n")
        fp.write("ADK::3\tG\tG\tT\n")
        fp.close()
        vpath = os.path.join(tdir,"testfile.filtered.vcf")
        vp = open(vpath, "w")
        vp.write("ADK::1\tG\n")
        vp.close()
        self.assertEqual(make_temp_matrix(vpath,fpath,"test"), {'ADK::1': 'G', 'ADK::2': '-', 'ADK::3': '-'})
        shutil.rmtree(tdir)
    def test_make_temp_matrix_no_matches(self):
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"testfile.matrix")
        fp = open(fpath, "w")
        fp.write("LocusID\tReference\tgenome1\tgenome2\n")
        fp.write("ADK::1\tA\tT\tT\n")
        fp.write("ADK::2\tT\tT\tT\n")
        fp.write("ADK::3\tG\tG\tT\n")
        fp.close()
        vpath = os.path.join(tdir,"testfile.filtered.vcf")
        vp = open(vpath, "w")
        vp.write("ADK::6\tA\n")
        vp.close()
        self.assertEqual(make_temp_matrix(vpath,fpath,"test"), {'ADK::1': '-', 'ADK::2': '-', 'ADK::3': '-', 'ADK::6': 'A'})
        shutil.rmtree(tdir)

class Test9(unittest.TestCase):
    def test_grab_names_basic_function(self):
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"test.filtered.vcf")
        fpath2 = os.path.join(tdir,"name_1.filtered.vcf")
        os.chdir("%s" % tdir)
        fp = open(fpath, "w")
        fp2 = open(fpath2, "w")
        fp.close()
        fp2.close()
        self.assertEqual(grab_names(), ['name_1', 'test'])
        os.chdir("%s" % curr_dir)
        shutil.rmtree(tdir)

class Test10(unittest.TestCase):
    def test_process_coverage_basic_function(self):
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"ECOLI_coverage.sample_summary")
        os.chdir("%s" % tdir)
        fp = open(fpath,"w")
        fp.write("sample_id       total   mean    granular_third_quartile granular_median granular_first_quartile %_bases_above_15\n")
        fp.write("ECOLI    2050    3.82    6       5       4       0.0\n")
        fp.write("Total    2050    3.82    N/A     N/A     N/A")
        fp.close()
        self.assertEqual(process_coverage("ECOLI"), {'ECOLI':'3.82'})
        os.chdir("%s" % curr_dir)
        shutil.rmtree(tdir)
    def test_process_coverage_missing_match(self):
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"ECOLI_coverage.sample_summary")
        os.chdir("%s" % tdir)
        fp = open(fpath,"w")
        fp.write("sample_id       total   mean    granular_third_quartile granular_median granular_first_quartile %_bases_above_15\n")
        fp.write("EOLI    2050    3.82    6       5       4       0.0\n")
        fp.write("Total    2050    3.82    N/A     N/A     N/A")
        fp.close()
        self.assertRaises(TypeError, process_coverage, "ECOLI")
        os.chdir("%s" % curr_dir)
        shutil.rmtree(tdir)

class Test11(unittest.TestCase):
    def test_find_two_basic_function(self):
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"all_patristic_distances.txt")
        os.chdir("%s" % tdir)
        fp = open(fpath,"w")
        fp.write("Distance between 'E2348_69_allexternalnucmer' and 'O157_H7_sakai_allexternalnucmer': 4.53192608862")
        fp.write("Distance between 'E2348_69_allexternalnucmer' and 'H10407_allexternalnucmer': 1.39030683167")
        fp.write("Distance between 'E2348_69_allexternalnucmer' and 'Reference': 1.29611949657")
        fp.close()
        self.assertRaises(TypeError, find_two, ['E2348_69_allexternalnucmer'])
        os.chdir("%s" % curr_dir)
        shutil.rmtree(tdir)
        
if __name__ == "__main__":
    unittest.main()
    main()
