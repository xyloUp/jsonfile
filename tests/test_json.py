from unittest import TestCase, main
from jsonfile import DynamicJSONObject, JSONObject

class JSONTests(TestCase):
    def setUp(self):
        self.f = JSONObject.from_file("tests\\sample.json")
    
    def test_obj(self):
        self.assertTrue(hasattr(self.f.as_object, "one"))
        
    def test_type(self):
        self.assertEqual(self.f.obj_type, list)
        
    def test_dict(self):
        self.assertEqual(self.f.as_dict, {"one": 1})
        
    def test_list(self):
        self.assertEqual(self.f.as_list, [[{"one": 1}]])
        
    def test_from_list(self):
        f = JSONObject([1, 2])
        self.assertEqual(f.json, [1, 2])
        
    def test_dynamic_mro(self):
        f = DynamicJSONObject(self.f)
        self.assertTrue(list in f.__class__.__mro__)
        
    def test_dynamic_to_json_obj(self):
        f = DynamicJSONObject(self.f)
        self.assertTrue(isinstance(f.as_json_object, JSONObject))
    
if __name__ == "__main__":
    main()