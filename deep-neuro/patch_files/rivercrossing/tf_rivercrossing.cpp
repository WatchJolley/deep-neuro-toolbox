/*
Copyright (c) 2018 Keele Technologies, Inc.
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
*/

#include <iostream>
#include <string>
#include "tensorflow/core/framework/op_kernel.h"
#include "tensorflow/core/framework/op.h"
#include "tensorflow/core/framework/shape_inference.h"
#include "tensorflow/core/framework/resource_mgr.h"
#include "tensorflow/core/framework/resource_op_kernel.h"
#include "tensorflow/core/lib/core/blocking_counter.h"
#include "tensorflow/core/lib/core/threadpool.h"
#include "tensorflow/core/platform/mutex.h"
#include "tf_env.h"
#include "rivercrossing.h"

#ifdef __USE_SDL
  #include <SDL.h>
#endif

using namespace tensorflow;
using namespace std;

class RivercrossingEnvironment : public Environment<float>, public StepInterface<int>
{
    public:
        int tensor_layers;
        string input_tensor;
        RivercrossingEnvironment(string tensor, int layers, int batch_size) //Complete
        {

            m_pInterfaces = new river::Environment[batch_size];
            m_numSteps.resize(batch_size, 0);
            input_tensor = tensor;
            tensor_layers = layers;

        }

        virtual ~RivercrossingEnvironment() { //Complete
            // cout << "River Enviroment Deleted" << endl;
            delete[] m_pInterfaces;
        }

        TensorShape get_observation_shape() override //Complete
        {
            // cout << "River Enviroment returned Observation Shape" << endl;

            return TensorShape({
                static_cast<int>(world::x),
                static_cast<int>(world::y),
                static_cast<int>(tensor_layers)
        });
            //InvalidArgumentError (see above for traceback): Input to reshape is a tensor with THIS values, but the requested shape requires a multiple of 1200
        }

        void get_observation(float *data, int idx) override //Complete
        {
            // cout << "River Enviroment returned Observation Inputs" << endl;
            assert(idx < m_numSteps.size());
            m_pInterfaces[idx].generate_neural_inputs(data, input_tensor);
        }

        TensorShape get_action_shape() override { //Complete
            return TensorShape();
        }

        float step(int idx, const int* action) override { //Complete
            // cout << "River Enviroment stepped" << endl;
            assert(idx < m_numSteps.size());
            m_numSteps[idx] = m_pInterfaces[idx].Update(action);

            if (is_done(idx))
            {
                return m_pInterfaces[idx].return_fitness();
            }
            return 0.0f;
        }

        bool is_done(int idx) override { //Complete
            // cout << "River Enviroment is been checked if done" << endl;
            return m_pInterfaces[idx].has_failed() || m_numSteps[idx] >= 150;
        }

        void reset(int i, int numNoops=0, int maxFrames=100000) override {
            // cout << "River Enviroment has been reset" << endl;
            m_pInterfaces[i].reset();
            m_numSteps[i] = 0;
        }

        string DebugString() override { return "RivercrossingEnvironment"; } //Complete
     private:
        river::Environment* m_pInterfaces;
        std::vector<int> m_numSteps;
};

class RivercrossingMakeOp : public EnvironmentMakeOp {
    public:
    explicit RivercrossingMakeOp(OpKernelConstruction* context) : EnvironmentMakeOp(context) {
        OP_REQUIRES_OK(context, context->GetAttr("input_tensor", &input_tensor));
        OP_REQUIRES_OK(context, context->GetAttr("num_layers", &num_layers));
    }

 private:
    virtual Status CreateResource(OpKernelContext* context, BaseEnvironment** ret) EXCLUSIVE_LOCKS_REQUIRED(mu_) {
        RivercrossingEnvironment* env = new RivercrossingEnvironment(input_tensor, num_layers, batch_size);
        if (env == nullptr)
            return errors::ResourceExhausted("Failed to allocate");
        *ret = env;

        const auto thread_pool = context->device()->tensorflow_cpu_worker_threads();
        const int num_threads = std::min(program::threads, batch_size);
        auto f = [&](int thread_id) {
            for(int b =thread_id; b < batch_size;b+=num_threads)
            {
                env->reset(b);
            }
        };

        BlockingCounter counter(num_threads-1);
        for (int i = 1; i < num_threads; ++i) {
            thread_pool->workers->Schedule([&, i]() {
                f(i);
                counter.DecrementCount();
            });
        }
        f(0); //Running scheduled thread
        counter.Wait();
        return Status::OK();
    }
    std::string input_tensor;
    int num_layers;
};

REGISTER_OP("RivercrossingMake")
    .Attr("input_tensor: string")
    .Attr("num_layers: int")
    .Attr("batch_size: int")
    .Attr("container: string = ''")
    .Attr("shared_name: string = ''")
    .Output("handle: resource")
    .SetIsStateful()
    .SetShapeFn(shape_inference::ScalarShape);

REGISTER_KERNEL_BUILDER(Name("RivercrossingMake").Device(DEVICE_CPU), RivercrossingMakeOp);