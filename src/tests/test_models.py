"""
This module contains an example test.

Tests should be placed in ``src/tests``, in modules that mirror your
project's structure, and in files named test_*.py. They are simply functions
named ``test_*`` which test a unit of logic.

To run the tests, run ``kedro test`` from the project root directory.
"""


import pytest
from kedro_graphql.models import DataSet, Parameter

class TestDataSet:

    def test_serialize(self):
        params = {"name": "text_in", 
                  "type": "text.TextDataset", 
                  "filepath": "/tmp/test_in.csv",
                  "load_args":[Parameter(**{
                    "name": "delimiter",
                    "value": "\t" 
                  })],
                  "save_args":[Parameter(**{
                    "name":"delimiter",
                    "value": "\t"  
                  })]}

        expected = {"text_in":{ 
                      "type": "text.TextDataset", 
                      "filepath": "/tmp/test_in.csv",
                      "load_args":{
                        "delimiter" :"\t" 
                      },
                      "save_args":{
                        "delimiter": "\t"  
                      },
                      "credentials": None
                    }
                   }

        d = DataSet(**params)
        output = d.serialize()
        print(output)
        assert output == expected
    
    def test_pre_signed_url_create_config_no_filepath(self):
        d = DataSet(name="text_in", config='{"type":"text.TextDataset"}')

        with pytest.raises(ValueError):
          output = d.pre_signed_url_create()
    
    def test_pre_signed_url_create_no_filepath(self):
        params = {"name": "text_in", 
          "type": "text.TextDataset",
          "load_args":[Parameter(**{
            "name": "delimiter",
            "value": "\t" 
          })],
          "save_args":[Parameter(**{
            "name":"delimiter",
            "value": "\t"  
          })]}
        
        d = DataSet(**params)
        
        with pytest.raises(ValueError):
          output = d.pre_signed_url_create()
    
    def test_pre_signed_url_create_no_s3_filepath(self):
        params = {"name": "text_in", 
          "type": "text.TextDataset",
          "filepath": "/tmp/test_in.csv", 
          "load_args":[Parameter(**{
            "name": "delimiter",
            "value": "\t" 
          })],
          "save_args":[Parameter(**{
            "name":"delimiter",
            "value": "\t"  
          })]}
        
        d = DataSet(**params)
        
        with pytest.raises(ValueError):
          output = d.pre_signed_url_create()
    
    def test_pre_signed_url_read_config_no_filepath(self):
        d = DataSet(name="text_in", config='{"type":"text.TextDataset"}')

        with pytest.raises(ValueError):
          output = d.pre_signed_url_create()
    
    def test_pre_signed_url_read_no_filepath(self):
        params = {"name": "text_in", 
          "type": "text.TextDataset", 
          "load_args":[Parameter(**{
            "name": "delimiter",
            "value": "\t" 
          })],
          "save_args":[Parameter(**{
            "name":"delimiter",
            "value": "\t"  
          })]}
        
        d = DataSet(**params)
        
        with pytest.raises(ValueError):
          output = d.pre_signed_url_read()
    
    def test_pre_signed_url_read_no_s3_filepath(self):
        params = {"name": "text_in", 
          "type": "text.TextDataset",
          "filepath": "/tmp/test_in.csv",  
          "load_args":[Parameter(**{
            "name": "delimiter",
            "value": "\t" 
          })],
          "save_args":[Parameter(**{
            "name":"delimiter",
            "value": "\t"  
          })]}
        
        d = DataSet(**params)
        
        with pytest.raises(ValueError):
          output = d.pre_signed_url_read()
    
    def test_does_exist_with_filepath(self, mock_text_in):
        params = {"name": "text_in", 
          "type": "text.TextDataset",
          "filepath": str(mock_text_in)}
        
        d = DataSet(**params)
        
        assert d.exists() == True
    
    def test_does_not_exist_with_filepath(self):
        params = {"name": "text_in", 
          "type": "text.TextDataset",
          "filepath": "/tmp/does_not_exist.csv"}
        
        d = DataSet(**params)
        
        assert d.exists() == False
    
    def test_does_exist_with_config(self, mock_text_in):
        params = {
            "name": "text_in",
            "config": f'{{"type": "text.TextDataset", "filepath": "{str(mock_text_in)}"}}'
        }
        print(params)

        d = DataSet(**params)
        assert d.exists() == True
    
    def test_does_not_exist_with_config(self):
        params = {
            "name": "text_in",
            "config": '{"type": "text.TextDataset", "filepath": "/tmp/does_not_exist.csv"}'
        }

        d = DataSet(**params)
        assert d.exists() == False
    
class TestParameter:

    def test_serialize_string(self):
        params = {
                    "name": "delimiter",
                    "value": "\t",
                    "type": "string"
                  }

        expected = {
                    "delimiter": "\t" 
                   }

        p = Parameter(**params)
        output = p.serialize()
        assert output == expected

    def test_serialize_int(self):
        params = {
                    "name": "delimiter",
                    "value": "1",
                    "type": "integer"
                  }

        expected = {
                    "delimiter": 1
                   }

        p = Parameter(**params)
        output = p.serialize()
        assert output == expected

    def test_serialize_int_exception(self):
        params = {
                    "name": "delimiter",
                    "value": "0.1",
                    "type": "integer"
                  }

        p = Parameter(**params)
        try:
            output = p.serialize()
        except ValueError as e:
            assert True

    def test_serialize_float(self):
        params = {
                    "name": "delimiter",
                    "value": "0.1",
                    "type": "float"
                  }

        expected = {
                    "delimiter": 0.1
                   }

        p = Parameter(**params)
        output = p.serialize()
        assert output == expected

    def test_serialize_float_exception(self):
        params = {
                    "name": "delimiter",
                    "value": "hello",
                    "type": "float"
                  }

        p = Parameter(**params)
        try:
            output = p.serialize()
        except ValueError as e:
            assert True
 
    def test_serialize_bool(self):

        params = {
                    "name": "delimiter",
                    "value": "true",
                    "type": "boolean"
                  }

        expected = {
                    "delimiter": True
                   }

        p = Parameter(**params)
        output = p.serialize()
        assert output == expected

        params = {
                    "name": "delimiter",
                    "value": "True",
                    "type": "boolean"
                  }

        expected = {
                    "delimiter": True
                   }

        p = Parameter(**params)
        output = p.serialize()
        assert output == expected

        params = {
                    "name": "delimiter",
                    "value": "false",
                    "type": "boolean"
                  }

        expected = {
                    "delimiter": False
                   }

        p = Parameter(**params)
        output = p.serialize()
        assert output == expected

        params = {
                    "name": "delimiter",
                    "value": "False",
                    "type": "boolean"
                  }

        expected = {
                    "delimiter": False
                   }

        p = Parameter(**params)
        output = p.serialize()
        assert output == expected

    def test_serialize_bool_exception(self):


        params = {
                    "name": "delimiter",
                    "value": "rue",
                    "type": "boolean"
                  }

        p = Parameter(**params)
        try:
            output = p.serialize()
        except ValueError as e:
            assert True
