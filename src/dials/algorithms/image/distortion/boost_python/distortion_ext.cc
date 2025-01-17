#include <boost/python.hpp>
#include <boost/python/def.hpp>
#include <dials/algorithms/image/distortion/ellipse.h>

namespace dials { namespace algorithms { namespace boost_python {

  using namespace boost::python;

  void export_create_elliptical_distortion_maps() {
    class_<CreateEllipticalDistortionMaps>("CreateEllipticalDistortionMaps", no_init)
      .def(init<const Panel &,
                scitbx::mat2<double>,
                scitbx::vec3<double>,
                scitbx::vec3<double>,
                scitbx::vec3<double>>(
        (arg("panel"), arg("ellipse_matrix"), arg("fast"), arg("slow"), arg("mid"))))
      .def("get_dx", &CreateEllipticalDistortionMaps::get_dx)
      .def("get_dy", &CreateEllipticalDistortionMaps::get_dy);
  }

  BOOST_PYTHON_MODULE(dials_algorithms_image_distortion_ext) {
    export_create_elliptical_distortion_maps();
  }

}}}  // namespace dials::algorithms::boost_python
